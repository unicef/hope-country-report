from typing import TYPE_CHECKING

import base64
import itertools
import json
import logging
import pickle
import types
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.files import File
from django.db import models, transaction
from django.db.models import JSONField
from django.urls import reverse
from django.utils import timezone
from django.utils.functional import cached_property, classproperty
from django.utils.text import slugify

import celery
import swapper
from celery import states
from celery.contrib.abortable import AbortableAsyncResult
from concurrency.api import disable_concurrency
from concurrency.fields import AutoIncVersionField
from django_celery_beat.models import PeriodicTask
from natural_keys import NaturalKeyModel
from sentry_sdk import capture_exception, configure_scope
from strategy_field.fields import StrategyField
from strategy_field.utils import fqn
from taggit.managers import TaggableManager

from hope_country_report.config.celery import app

from ...state import state
from ...utils.perf import profile
from ..core.models import CountryOffice
from ..tenant.db import TenantModel
from .exceptions import QueryRunCanceled, QueryRunError
from .json import PQJSONEncoder
from .manager import PowerQueryManager
from .processors import mimetype_map, ProcessorStrategy, registry, ToHTML, TYPE_LIST, TYPES
from .utils import dict_hash, is_valid_template, to_dataset

if TYPE_CHECKING:
    from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple

    from django.db.models import QuerySet

    from ...types.django import AnyModel
    from ...types.pq import QueryMatrixResult, ReportResult
    from .celery_tasks import PowerQueryTask

logger = logging.getLogger(__name__)

MIMETYPES = [(k, v) for k, v in mimetype_map.items()]


def validate_queryargs(value: "Any") -> None:
    try:
        if not isinstance(value, dict):
            raise ValidationError("QueryArgs must be a dict")
        product = list(itertools.product(*value.values()))
        [dict(zip(value.keys(), e)) for e in product]
    except ValidationError:
        raise
    except Exception as e:
        raise ValidationError(
            "%(exc)s: " "%(value)s is not a valid QueryArgs",
            params={"value": value, "exc": e},
        )


class CeleryEnabled(models.Model):
    # QUEUED (task exists in Redis but unkonw to Celery)
    # CANCELED (task is canceled BEFORE worker fetch it)
    # PENDING (waiting for execution or unknown task id)
    # STARTED (task has been started)
    # SUCCESS (task executed successfully)
    # FAILURE (task execution resulted in exception)
    # RETRY (task is being retried)
    # REVOKED (task has been revoked)
    SCHEDULED = frozenset({states.PENDING, states.RECEIVED, states.STARTED, states.RETRY, "QUEUED"})
    QUEUED = "QUEUED"
    CANCELED = "CANCELED"

    version = AutoIncVersionField()
    sentry_error_id = models.CharField(max_length=400, blank=True, null=True)
    error_message = models.CharField(max_length=400, blank=True, null=True)
    last_run = models.DateTimeField(null=True, blank=True)

    curr_async_result_id = models.CharField(
        max_length=36, blank=True, null=True, help_text="Current (active) AsyncResult is"
    )
    last_async_result_id = models.CharField(
        max_length=36, blank=True, null=True, help_text="Latest executed AsyncResult is"
    )

    celery_task_name: str = "<define `celery_task_name`>"

    class Meta:
        abstract = True

    def get_celery_queue_position(self) -> int:
        from hope_country_report.config.celery import app

        with app.pool.acquire(block=True) as conn:
            tasks = conn.default_channel.client.lrange(settings.CELERY_TASK_DEFAULT_QUEUE, 0, -1)
        for i, task in enumerate(tasks, 1):
            j = json.loads(task)
            if j["headers"]["id"] == self.curr_async_result_id:
                return i
        return 0

    def celery_queue_status(self) -> "Dict[str, int]":
        with app.pool.acquire(block=True) as conn:
            tasks = conn.default_channel.client.lrange(settings.CELERY_TASK_DEFAULT_QUEUE, 0, 1)
            revoked = list(conn.default_channel.client.smembers(settings.CELERY_TASK_REVOKED_QUEUE))
            pending = len(tasks)
            canceled = 0
            pending_tasks = [json.loads(task)["headers"]["id"].encode() for task in tasks]
            for task_id in pending_tasks:
                if task_id in revoked:
                    pending -= 1
                    canceled += 1

            for rem in revoked:
                if rem not in pending_tasks:
                    conn.default_channel.client.srem(settings.CELERY_TASK_REVOKED_QUEUE, rem)
            return {"size": len(tasks), "pending": pending, "canceled": canceled, "revoked": len(revoked)}

    @cached_property
    def async_result(self) -> "AbortableAsyncResult|None":
        if self.curr_async_result_id:
            return AbortableAsyncResult(self.curr_async_result_id, app=celery.current_app)
        else:
            return None

    @property
    def queue_info(self) -> "Dict[str, Any]":
        with app.pool.acquire(block=True) as conn:
            tasks = conn.default_channel.client.lrange(settings.CELERY_TASK_DEFAULT_QUEUE, 0, -1)

        for task in tasks:
            j = json.loads(task)
            if j["headers"]["id"] == self.async_result.id:
                j["body"] = json.loads(base64.b64decode(j["body"]))
                return j
        return {"id": "NotFound"}

    @property
    def task_info(self) -> "Dict[str, Any]":
        if self.async_result:
            info = self.async_result._get_task_meta()
            result, task_status = info["result"], info["status"]
            if task_status == "STARTED":
                started_at = result.get("start_time", 0)
            else:
                started_at = 0
            last_update = info["date_done"]
            if isinstance(result, Exception):
                error = str(result)
            elif task_status == "REVOKED":
                error = "Query execution cancelled."
            else:
                error = ""

            if task_status == "SUCCESS" and not error:
                query_result_id = result
            else:
                query_result_id = None
            return {
                **info,
                # "id": self.async_result.id,
                "last_update": last_update,
                "started_at": started_at,
                "status": task_status,
                "error": error,
                "query_result_id": query_result_id,
            }

    @classproperty
    def task_handler(cls) -> "Callable[Any, Any]":
        from . import celery_tasks

        return getattr(celery_tasks, cls.celery_task_name)

    def is_queued(self) -> bool:
        from hope_country_report.config.celery import app

        with app.pool.acquire(block=True) as conn:
            tasks = conn.default_channel.client.lrange(settings.CELERY_TASK_DEFAULT_QUEUE, 0, -1)
        for task in tasks:
            j = json.loads(task)
            if j["headers"]["id"] == self.curr_async_result_id:
                return True
        return False

    def is_canceled(self) -> bool:
        with app.pool.acquire(block=True) as conn:
            return conn.default_channel.client.sismember(settings.CELERY_TASK_REVOKED_QUEUE, self.curr_async_result_id)

    @property
    def status(self) -> str:
        try:
            if self.curr_async_result_id:
                if self.is_canceled():
                    return "CANCELED"

                result = self.async_result.state
                if result == "PENDING":
                    if self.is_queued():
                        result = "QUEUED"
                    else:
                        result = "Not scheduled"
            else:
                result = "Not scheduled"
            return result
        except Exception as e:
            return str(e)

    def queue(self) -> str | None:
        if self.status not in self.SCHEDULED:
            ver = self.version
            res = self.task_handler.delay(self.id, self.version)
            with disable_concurrency(self):
                self.curr_async_result_id = res.id
                self.save(update_fields=["curr_async_result_id"])
            assert self.version == ver
            return self.curr_async_result_id
        return None

    def terminate(self) -> None:
        if self.status in ["QUEUED", "PENDING"]:
            with app.pool.acquire(block=True) as conn:
                conn.default_channel.client.sadd(
                    settings.CELERY_TASK_REVOKED_QUEUE, self.curr_async_result_id, self.curr_async_result_id
                )
        else:
            app.control.revoke(self.curr_async_result_id, terminate=True)

    @classmethod
    def discard_all(cls) -> None:
        app.control.discard_all()
        cls.objects.update(curr_async_result_id=None)
        with app.pool.acquire(block=True) as conn:
            conn.default_channel.client.delete(settings.CELERY_TASK_REVOKED_QUEUE)

    @classmethod
    def purge(cls) -> None:
        app.control.purge()


class PowerQueryModel(TenantModel):
    class Meta:
        abstract = True

    objects = PowerQueryManager()


#
# class ProjectRelatedModel(PowerQueryModel):
#     project = models.ForeignKey(
#         swapper.get_model_name("power_query", "Project"), blank=True, on_delete=models.CASCADE, null=True
#     )
#
#     objects = PowerQueryManager()
#
#     class Meta:
#         abstract = True
#
#     class Tenant:
#         tenant_filter_field = "project"


class Parametrizer(NaturalKeyModel, models.Model):
    country_office = models.ForeignKey(CountryOffice, on_delete=models.CASCADE, blank=True, null=True)
    code = models.SlugField(max_length=255, unique=True, editable=False)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(max_length=255, null=True, blank=True)
    value = models.JSONField(default=dict, blank=False, validators=[validate_queryargs])
    system = models.BooleanField(blank=True, default=False, editable=False)
    source = models.ForeignKey("Query", blank=True, null=True, on_delete=models.CASCADE, related_name="+")

    class Meta:
        verbose_name_plural = "Arguments"
        verbose_name = "Arguments"

    class Tenant:
        tenant_filter_field = "country_office"

    def clean(self) -> None:
        validate_queryargs(self.value)

    def get_matrix(self) -> "List[Dict[str,str]]":
        if isinstance(self.value, dict):
            product = list(itertools.product(*self.value.values()))
            return [dict(zip(self.value.keys(), e)) for e in product]
        else:
            param = slugify(self.code).replace("-", "_")
            return [{param: e} for e in self.value]

    def save(
        self,
        force_insert: bool = False,
        force_update: bool = False,
        using: str | None = None,
        update_fields: "Iterable[str] | None" = None,
    ) -> None:
        if not self.code:
            self.code = slugify(self.name)
        super().save(force_insert, force_update, using, update_fields)

    def refresh(self) -> None:
        if self.source:
            out, __ = self.source.run(use_existing=True)
            self.value = list(out.data)
            self.save()

    def __str__(self) -> str:
        return self.name


class BaseProject(models.Model):
    name = models.CharField(max_length=200)

    class Meta:
        abstract = True


class Project(models.Model):
    name = models.CharField(max_length=200)

    class Meta:
        swappable = swapper.swappable_setting("power_query", "Project")


class Query(CeleryEnabled, models.Model):
    country_office = models.ForeignKey(CountryOffice, on_delete=models.CASCADE, blank=True, null=True)

    datasets: "QuerySet[Dataset]"
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    parent = models.ForeignKey("self", blank=True, null=True, on_delete=models.CASCADE)
    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, blank=True, null=True, related_name="queries")
    target = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    code = models.TextField(default="result=conn.all()", blank=True)
    info = JSONField(default=dict, blank=True, encoder=PQJSONEncoder)
    parametrizer = models.ForeignKey(Parametrizer, on_delete=models.CASCADE, blank=True, null=True)
    active = models.BooleanField(default=True)

    celery_task_name = "run_background_query"

    def __str__(self) -> str:
        return self.name or ""

    class Meta:
        verbose_name_plural = "Queries"
        ordering = ("name",)

    class Tenant:
        tenant_filter_field = "country_office"

    def save(
        self,
        force_insert: bool = False,
        force_update: bool = False,
        using: str | None = None,
        update_fields: "Iterable[str] | None" = None,
    ) -> None:
        if not self.code:
            self.code = "result=conn.all().order_by('pk')"
        super().save(force_insert, force_update, using, update_fields)

    @property
    def silk_name(self) -> str:
        return "Query %s #%s" % (self.name, self.pk)

    def _invoke(self, query_id: int, arguments: "Dict[str, Any]") -> "Tuple[Any, Any]":
        query = Query.objects.get(id=query_id)
        result = query.run(persist=False, arguments=arguments, use_existing=True)
        return result

    def update_results(self, results: "QueryMatrixResult") -> None:
        self.info["last_run_results"] = results
        self.error_message = results.get("error_message", "")
        self.sentry_error_id = results.get("sentry_error_id", "")
        self.last_run = timezone.now()
        self.save()

    def execute_matrix(self, persist: bool = True, running_task: "PowerQueryTask|None" = None) -> "QueryMatrixResult":
        if self.parametrizer:
            args = self.parametrizer.get_matrix()
            if not args:
                args = [{}]
                # raise ValueError("No valid arguments provided")
        else:
            args = [{}]
        self.error_message = None
        self.sentry_error_id = None
        self.last_run = None
        self.info = {}
        self.running_task = running_task
        results: "QueryMatrixResult" = {}
        with configure_scope() as scope:
            scope.set_tag("power_query", True)
            scope.set_tag("power_query.name", self.name)
            with transaction.atomic():
                transaction.on_commit(lambda: self.update_results(results))
                for a in args:
                    try:
                        dataset, info = self.run(persist, a, running_task=self.running_task)
                        results[str(a)] = dataset.pk
                    except QueryRunCanceled:
                        raise
                    except QueryRunError as e:
                        logger.exception(e)
                        err = capture_exception(e)
                        results["sentry_error_id"] = str(err)
                        results["error_message"] = str(e)
                        raise
                self.datasets.exclude(pk__in=[dpk for dpk in results.values() if isinstance(dpk, int)]).delete()
        return results

    def run(
        self,
        persist: bool = False,
        arguments: "Dict[str,Any]|None" = None,
        use_existing: bool = False,
        preview: bool = False,
        running_task: "PowerQueryTask|None" = None,
        **kwargs: "Dict[str, Any]",
    ) -> "Tuple[Dataset, Dict[str,Any]]":
        model = self.target.model_class()
        connections: Dict[str, QuerySet[AnyModel]] = {}
        return_value: Tuple[Dataset, Dict[str, Any]]
        if state.tenant:
            connections["QueryManager"] = Query.objects.filter(country_office=state.tenant)
        else:
            connections["QueryManager"] = Query.objects.filter()
        debug = []
        try:
            self.aborted = False

            def is_aborted(self: Query) -> bool:
                return self.aborted or running_task.is_aborted()

            self.is_aborted = types.MethodType(is_aborted, self)

            with profile() as perfs:
                locals_ = {
                    "conn": model._default_manager.using(settings.POWER_QUERY_DB_ALIAS),
                    "self": self,
                    "args": arguments,
                    "arguments": arguments,
                    "to_dataset": to_dataset,
                    "invoke": self._invoke,
                    "debug": lambda *a: debug.append((timezone.now().strftime("%H:%M:%S"), *a)),
                    "task": running_task,
                    **kwargs,
                    **connections,
                }
                signature = dict_hash({"query": self.pk, **(arguments if arguments else {})})
                if not preview and use_existing and (ds := Dataset.objects.filter(query=self, hash=signature).first()):
                    return_value = ds, ds.extra
                else:
                    with state.set(preview=preview):
                        exec(self.code, globals(), locals_)

                    result = locals_.get("result", None)
                    extra = locals_.get("extra", None)
                    info = {
                        "type": type(result).__name__,
                        "arguments": arguments,
                        "perfs": perfs,
                        "debug": debug,
                    }
                    defaults = {
                        "size": len(result) if result else 0,
                        "info": info,
                        "last_run": timezone.now(),
                        "value": pickle.dumps(result),
                        "extra": pickle.dumps(extra),
                    }
                    if persist:
                        dataset, __ = Dataset.objects.update_or_create(query=self, hash=signature, defaults=defaults)
                    else:
                        dataset = Dataset(query=self, hash=signature, **defaults)

                    return_value = dataset, extra
        except Exception:
            raise
        return return_value


class Dataset(PowerQueryModel, models.Model):
    hash = models.CharField(unique=True, max_length=200, editable=False)
    last_run = models.DateTimeField(null=True, blank=True)
    description = models.CharField(max_length=100)
    query = models.ForeignKey(Query, on_delete=models.CASCADE, related_name="datasets")
    value = models.BinaryField(null=True, blank=True)
    file = models.FileField(null=True, blank=True, upload_to="datasets")

    size = models.IntegerField(default=0)
    info = JSONField(default=dict, blank=True)
    extra = models.BinaryField(null=True, blank=True, help_text="Any other attribute to pass to the formatter")

    class Tenant:
        tenant_filter_field = "query__country_office"

    def __str__(self) -> str:
        return f"Result of {self.query.name} {self.arguments}"

    @property
    def country_office(self) -> "CountryOffice":
        return self.query.country_office

    @property
    def data(self) -> "Any":
        return pickle.loads(self.value)

    @property
    def arguments(self) -> "Dict[str, int|str]":
        return self.info.get("arguments", {})


class ReportTemplate(models.Model):
    country_office = models.ForeignKey(CountryOffice, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True, unique=True)
    doc = models.FileField()
    suffix = models.CharField(max_length=20)
    content_type = models.CharField(max_length=200, choices=MIMETYPES)  # type: ignore # internal mypy error

    class Tenant:
        tenant_filter_field = "country_office"

    @classmethod
    def load(cls) -> None:
        template_dir = Path(settings.PACKAGE_DIR) / "apps" / "power_query" / "templates"
        for filename in (template_dir / "reports").glob("*.*"):
            if is_valid_template(filename):
                record_name = f"{slugify(filename.stem)}{filename.suffix}"
                ReportTemplate.objects.get_or_create(
                    name=record_name,
                    defaults={
                        "doc": File(filename.open("rb"), record_name),
                        "content_type": filename.suffix,
                        "suffix": filename.suffix,
                    },
                )

    def save(
        self,
        force_insert: bool = False,
        force_update: bool = False,
        using: str | None = None,
        update_fields: "Iterable[str] | None" = None,
    ) -> None:
        self.suffix = Path(self.doc.name).suffix
        super().save(force_insert, force_update, using, update_fields)

    def __str__(self) -> str:
        return str(self.name)


class Formatter(models.Model):
    country_office = models.ForeignKey(CountryOffice, on_delete=models.CASCADE, blank=True, null=True)

    processor: "ProcessorStrategy"
    name = models.CharField(max_length=255, unique=True)
    code = models.TextField(blank=True, null=True)
    template = models.ForeignKey(ReportTemplate, on_delete=models.CASCADE, blank=True, null=True)

    content_type = models.CharField(max_length=200, choices=MIMETYPES)
    processor = StrategyField(registry=registry, default=fqn(ToHTML))
    type = models.IntegerField(choices=TYPES, default=TYPE_LIST)

    class Tenant:
        tenant_filter_field = "country_office"

    def __str__(self) -> str:
        return self.name

    def clean(self) -> None:
        if self.code and self.template:
            raise ValidationError("You cannot set both 'template' and 'code'")
        if self.processor.mime_type and self.processor.mime_type != self.content_type:
            raise ValidationError(f"Incompatible Content-Type: {self.processor.mime_type} {self.content_type}")
        self.processor.validate()

    def render(self, context: "Dict[str, Any]") -> bytearray:
        if self.type == TYPE_LIST:
            return self.processor.process(context)
        else:
            ret = bytearray()
            ds = context.pop("dataset")
            for page, entry in enumerate(ds.data, 1):
                context["page"] = page
                context["record"] = entry
                ret.extend(self.processor.process(context))
            return ret

    def save(
        self,
        force_insert: bool = False,
        force_update: bool = False,
        using: "str|None" = None,
        update_fields: "Iterable[str]|None" = None,
    ) -> None:
        if not self.content_type:
            self.content_type = self.processor.content_type
        super().save(force_insert, force_update, using, update_fields)


class Report(CeleryEnabled, models.Model):
    country_office = models.ForeignKey(CountryOffice, on_delete=models.CASCADE, blank=True, null=True)

    title = models.CharField(max_length=255, blank=False, null=False, verbose_name="Report Title")
    name = models.CharField(max_length=255, blank=True, null=True)
    query = models.ForeignKey(Query, on_delete=models.CASCADE)
    description = models.TextField(max_length=255, null=True, blank=True, default="")

    formatters = models.ManyToManyField(Formatter, null=False, blank=False)
    active = models.BooleanField(default=True)
    owner = models.ForeignKey(get_user_model(), blank=True, null=True, on_delete=models.CASCADE, related_name="+")
    limit_access_to = models.ManyToManyField(get_user_model(), blank=True, related_name="+")
    schedule = models.ForeignKey(PeriodicTask, blank=True, null=True, on_delete=models.SET_NULL, related_name="reports")
    last_run = models.DateTimeField(null=True, blank=True)
    validity_days = models.IntegerField(default=365)

    tags = TaggableManager(blank=True)
    celery_task_name = "refresh_report"

    class Tenant:
        tenant_filter_field = "country_office"

    def save(
        self,
        force_insert: bool = False,
        force_update: bool = False,
        using: "Optional[Any]" = None,
        update_fields: "Optional[Any]" = None,
    ) -> None:
        if not self.name:
            self.name = slugify(self.title)
        super().save(force_insert, force_update, using, update_fields)

    def execute(self, run_query: bool = False) -> "ReportResult":
        # TODO: refactor that
        query: Query = self.query
        result: "ReportResult" = []
        if run_query:
            query.execute_matrix()
        for formatter in self.formatters.all():
            for dataset in query.datasets.all():
                if not dataset.size:
                    continue
                try:
                    context = dataset.arguments
                    if dataset.extra:
                        context.update(pickle.loads(dataset.extra) or {})

                    try:
                        title = self.title.format(**context)
                    except KeyError:
                        title = self.title
                    with profile() as perfs:
                        output = formatter.render(
                            {
                                "dataset": dataset,
                                "report": self,
                                "title": title,
                                "context": context,
                            }
                        )
                    res, __ = ReportDocument.objects.update_or_create(
                        report=self,
                        dataset=dataset,
                        defaults={
                            "title": title,
                            "content_type": formatter.content_type,
                            "output": pickle.dumps(output),
                            "arguments": dataset.arguments,
                            "info": perfs,
                        },
                    )
                    result.append((res.pk, len(res.output)))
                except Exception as e:
                    logger.exception(e)
                    result.append((dataset.pk, str(e)))
        self.last_run = timezone.now()
        if not result:
            result = ["No Dataset available"]
        return result

    def __str__(self) -> str:
        return self.name or ""

    def get_absolute_url(self) -> str:
        return reverse("power_query:report", args=[self.pk])


class ReportDocumentManager(PowerQueryManager["ReportDocument"]):
    def get_queryset(self) -> "models.QuerySet[ReportDocument]":
        return super().get_queryset().select_related("report")


class ReportDocument(PowerQueryModel, models.Model):
    timestamp = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=300)
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name="documents")
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    output = models.BinaryField(null=True, blank=True)
    arguments = models.JSONField(default=dict, encoder=PQJSONEncoder)
    limit_access_to = models.ManyToManyField(get_user_model(), blank=True, related_name="+")
    content_type = models.CharField(max_length=200, choices=MIMETYPES)  # type: ignore # internal mypy error
    info = models.JSONField(default=dict, blank=True, null=False)
    objects = ReportDocumentManager()

    class Meta:
        unique_together = ("report", "dataset")

    class Tenant:
        tenant_filter_field = "report__query__project"

    def __str__(self) -> str:
        return self.title

    @cached_property
    def country_office(self) -> "CountryOffice":
        return self.report.country_office

    @cached_property
    def data(self) -> "Any":
        return pickle.loads(self.output)

    @cached_property
    def size(self) -> int:
        return len(self.output)

    def get_absolute_url(self) -> str:
        return reverse("power_query:document", args=[self.report.pk, self.pk])
