from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING, Union

import itertools
import logging
import pickle
from datetime import datetime

from django.apps import apps as django_apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import JSONField, Q
from django.template import Context, Template
from django.urls import reverse
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.text import slugify

import celery
import swapper
from celery import states
from celery.result import AsyncResult
from natural_keys import NaturalKeyModel
from sentry_sdk import capture_exception, configure_scope
from taggit.managers import TaggableManager

from ...state import state
from ...utils.perf import profile
from ..tenant.db import TenantModel
from ..tenant.exceptions import InvalidTenantError
from ..tenant.utils import get_selected_tenant, must_tenant
from .exceptions import QueryRunError
from .json import PQJSONEncoder
from .utils import dict_hash, to_dataset
from .validators import FrequencyValidator

if TYPE_CHECKING:
    from django.db.models import QuerySet

    DocumentResult = Tuple[int, Union[str, int]]
    ReportResult = List[Union[DocumentResult, Any, str]]
    QueryResult = Tuple[Any, Dict]
    QueryMatrixResult = Dict[str, Union[int, str]]


logger = logging.getLogger(__name__)

mimetype_map = {
    "csv": "text/csv",
    "html": "text/html",
    "json": "application/json",
    "txt": "text/plain",
    "xls": "application/vnd.ms-excel",
    "xml": "application/xml",
    "yaml": "text/yaml",
    "pdf": "application/pdf",
}

MIMETYPES = ((k, v) for k, v in mimetype_map.items())


def validate_queryargs(value: Any) -> None:
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
    SCHEDULED = frozenset({states.PENDING, states.RECEIVED, states.STARTED, states.RETRY})

    celery_task = models.CharField(max_length=36, blank=True, null=True)

    class Meta:
        abstract = True

    def status(self) -> str:
        if self.celery_task:
            try:
                result = self.async_result.state
            except Exception as e:
                result = str(e)
        else:
            result = "Not scheduled"
        return result

    @property
    def async_result(self) -> Optional[AsyncResult]:
        if self.celery_task and self.status not in self.SCHEDULED:
            return AsyncResult(self.celery_task, app=celery.current_app)
        else:
            return None

    def queue(self) -> Optional[str]:
        if self.status not in self.SCHEDULED:
            task_id = self._queue()
            if not task_id:
                raise NotImplementedError("`_queue` not properly implemented")
            return task_id
        return None

    def _queue(self) -> str:
        return ""


class PowerQueryManager(models.Manager):
    def get_tenant_filter(self):
        if not must_tenant():
            return Q()
        _filter = {}
        tenant_filter_field = self.model.Tenant.tenant_filter_field
        if not tenant_filter_field:
            raise ValueError(
                f"Set 'tenant_filter_field' on {self} or override `get_queryset()` to enable queryset filtering"
            )

        if tenant_filter_field == "__all__":
            return {}
        elif tenant_filter_field == "__none__":
            return {"pk__lt": -1}
        elif tenant_filter_field == "__shared__":
            if active_tenant := get_selected_tenant():
                _filter = Q(**{tenant_filter_field: active_tenant}) or Q({f"{tenant_filter_field}__isnull": True})
        else:
            active_tenant = get_selected_tenant()
            if not active_tenant:
                raise InvalidTenantError
            _filter = Q(**{tenant_filter_field: active_tenant})
        return _filter

    def get_queryset(self):
        flt = self.get_tenant_filter()
        if flt:
            state.filters.append(str(flt))
        return super().get_queryset().filter(flt)


class PowerQueryModel(TenantModel):
    class Meta:
        abstract = True

    objects = PowerQueryManager()


class ProjectRelatedModel(PowerQueryModel):
    project = models.ForeignKey(
        swapper.get_model_name("power_query", "Project"), blank=True, on_delete=models.CASCADE, null=True
    )

    objects = PowerQueryManager()

    class Meta:
        abstract = True

    class Tenant:
        tenant_filter_field = "project"


class Parametrizer(NaturalKeyModel, ProjectRelatedModel, models.Model):
    code = models.SlugField(max_length=255, unique=True, editable=False)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(
        max_length=255,
        null=True,
        blank=True,
    )
    value = models.JSONField(default=dict, blank=False, validators=[validate_queryargs])
    system = models.BooleanField(blank=True, default=False, editable=False)
    source = models.ForeignKey("Query", blank=True, null=True, on_delete=models.CASCADE, related_name="+")

    class Meta:
        verbose_name_plural = "Arguments"
        verbose_name = "Arguments"

    class Tenant:
        tenant_filter_field = "project"

    def clean(self) -> None:
        validate_queryargs(self.value)

    def get_matrix(self) -> List[Dict]:
        product = list(itertools.product(*self.value.values()))
        return [dict(zip(self.value.keys(), e)) for e in product]

    def save(
        self,
        force_insert: bool = False,
        force_update: bool = False,
        using: Optional[Any] = None,
        update_fields: Optional[Any] = None,
    ) -> None:
        if not self.code:
            self.code = slugify(self.name)
        super().save(force_insert, force_update, using, update_fields)

    def refresh(self) -> None:
        if self.source:
            out, __ = self.source.run(use_existing=True)
            self.value = out
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


class Query(ProjectRelatedModel, CeleryEnabled, models.Model):
    datasets: "QuerySet[Dataset]"
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    parent = models.ForeignKey("self", blank=True, null=True, on_delete=models.CASCADE)
    owner = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, blank=True, null=True, related_name="power_queries"
    )
    target = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    code = models.TextField(default="result=conn.all()", blank=True)
    info = JSONField(default=dict, blank=True, encoder=PQJSONEncoder)
    parametrizer = models.ForeignKey(Parametrizer, on_delete=models.CASCADE, blank=True, null=True)
    sentry_error_id = models.CharField(max_length=400, blank=True, null=True)
    error_message = models.CharField(max_length=400, blank=True, null=True)

    last_run = models.DateTimeField(null=True, blank=True)

    active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name or ""

    class Meta:
        verbose_name_plural = "Power Queries"
        ordering = ("name",)

    class Tenant:
        tenant_filter_field = "project"

    def save(
        self,
        force_insert: bool = False,
        force_update: bool = False,
        using: "Optional[Any]" = None,
        update_fields: "Optional[Any]" = None,
    ) -> None:
        if not self.code:
            self.code = "result=conn.all().order_by('pk')"
        super().save(force_insert, force_update, using, update_fields)

    @property
    def silk_name(self):
        return "Query %s #%s" % (self.name, self.pk)

    def _invoke(self, query_id: int, arguments: Dict) -> Tuple[Any, Any]:
        query = Query.objects.get(id=query_id)
        result = query.run(persist=False, arguments=arguments, use_existing=True)
        return result

    def update_results(self, results: "QueryMatrixResult") -> None:
        self.info["last_run_results"] = results
        self.error_message = results.get("error_message", "")
        self.sentry_error_id = results.get("sentry_error_id", "")
        self.last_run = timezone.now()
        self.save()

    def execute_matrix(self, persist: bool = True, **kwargs: Any) -> "QueryMatrixResult":
        if self.parametrizer:
            args = self.parametrizer.get_matrix()
            if not args:
                raise ValueError("No valid arguments provided")
        else:
            args = [{}]
        self.error_message = None
        self.sentry_error_id = None
        self.last_run = None
        self.info = {}

        results: "QueryMatrixResult" = {"timestamp": datetime.strftime(timezone.now(), "%Y-%m-%d %H:%M")}
        with configure_scope() as scope:
            scope.set_tag("power_query", True)
            scope.set_tag("power_query.name", self.name)
            with transaction.atomic():
                transaction.on_commit(lambda: self.update_results(results))
                for a in args:
                    try:
                        dataset, __ = self.run(persist, a)
                        if isinstance(dataset, Dataset):
                            results[str(a)] = dataset.pk
                        else:
                            results[str(a)] = str(len(dataset))

                    except QueryRunError as e:
                        logger.exception(e)
                        err = capture_exception(e)
                        results["sentry_error_id"] = str(err)
                        results["error_message"] = str(e)
                self.datasets.exclude(pk__in=[dpk for dpk in results.values() if isinstance(dpk, int)]).delete()
        return results

    def run(
        self, persist: bool = False, arguments: "Dict|None" = None, use_existing: bool = False, preview: bool = False
    ) -> "QueryResult":
        model = self.target.model_class()
        connections_model = [get_user_model()]
        if settings.POWER_QUERY_EXTRA_CONNECTIONS:
            connections_model.extend(
                [django_apps.get_model(label2model) for label2model in settings.POWER_QUERY_EXTRA_CONNECTIONS]
            )
        connections = {
            f"{model._meta.object_name}Manager": model._default_manager.using(settings.POWER_QUERY_DB_ALIAS)
            for model in connections_model
        }
        return_value: QueryResult
        if self.owner.is_superuser:
            connections["QueryManager"] = Query.objects.filter()
        else:
            connections["QueryManager"] = Query.objects.filter(owner=self.owner)
        debug = []
        try:
            with profile() as perfs:
                locals_ = {
                    "conn": model._default_manager.using(settings.POWER_QUERY_DB_ALIAS),
                    "query": self,
                    "args": arguments,
                    "arguments": arguments,
                    "invoke": self._invoke,
                    "debug": lambda *a: debug.append((timezone.now().strftime("%H:%M:%S"), *a)),
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
                        "extra": extra,
                    }
                    if result and persist:
                        dataset, __ = Dataset.objects.update_or_create(
                            query=self,
                            hash=signature,
                            defaults={
                                "info": info,
                                "last_run": timezone.now(),
                                "value": pickle.dumps(result),
                                "extra": pickle.dumps(extra),
                            },
                        )
                        return_value = dataset, info
                    else:
                        return_value = result, info
        except Exception as e:
            raise QueryRunError(e) from e
        return return_value

    def _queue(self) -> str:
        from .celery_tasks import run_background_query

        res = run_background_query.delay(self.id)
        self.celery_task = res.id
        self.save()
        return res.id


class Dataset(PowerQueryModel, models.Model):
    hash = models.CharField(unique=True, max_length=200, editable=False)
    last_run = models.DateTimeField(null=True, blank=True)
    description = models.CharField(max_length=100)
    query = models.ForeignKey(Query, on_delete=models.CASCADE, related_name="datasets")
    value = models.BinaryField(null=True, blank=True)
    file = models.FileField(null=True, blank=True, upload_to="datasets")

    info = JSONField(default=dict, blank=True)
    extra = models.BinaryField(null=True, blank=True, help_text="Any other attribute to pass to the formatter")

    class Tenant:
        tenant_filter_field = "query__project"

    def __str__(self) -> str:
        return f"Result of {self.query.name} {self.arguments}"

    @property
    def data(self) -> Any:
        return pickle.loads(self.value)

    @property
    def size(self) -> int:
        return len(self.value)

    @property
    def arguments(self) -> Dict:
        return self.info.get("arguments", {})


class PDFForm(ProjectRelatedModel, models.Model):
    name = models.CharField(max_length=255, blank=True, null=True, unique=True)
    pfd = models.FileField()

    def render(self):
        pass


class Formatter(ProjectRelatedModel, models.Model):
    name = models.CharField(max_length=255, unique=True)
    content_type = models.CharField(max_length=5, choices=MIMETYPES)  # type: ignore # internal mypy error
    code = models.TextField(blank=True, null=True)
    template = models.ForeignKey(PDFForm, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self) -> str:
        return self.name

    def clean(self):
        if self.content_type == "pdf" and not self.template:
            raise ValidationError({"You must provide a template with PDF ContentType"})

    def render(self, context: Dict) -> str:
        if self.content_type == "xls":
            dt = to_dataset(context["dataset"].data)
            return dt.export("xls")

        elif self.content_type == "pdf":
            raise NotImplementedError

        if self.code:
            tpl = Template(self.code)
        elif self.content_type == "json":
            dt = to_dataset(context["dataset"].data)
            return dt.export("json")
        elif self.content_type == "yaml":
            dt = to_dataset(context["dataset"].data)
            return dt.export("yaml")
        else:
            raise ValueError("Unable to render")

        return tpl.render(Context(context))


class Report(ProjectRelatedModel, CeleryEnabled, models.Model):
    title = models.CharField(max_length=255, blank=False, null=False, verbose_name="Report Title")
    name = models.CharField(max_length=255, blank=True, null=True)
    query = models.ForeignKey(Query, on_delete=models.CASCADE)
    formatter = models.ForeignKey(Formatter, on_delete=models.CASCADE, blank=True, null=True)
    active = models.BooleanField(default=True)
    owner = models.ForeignKey(
        get_user_model(),
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="+",
    )
    limit_access_to = models.ManyToManyField(get_user_model(), blank=True, related_name="+")
    frequence = models.CharField(
        max_length=30,
        null=True,
        blank=True,
        help_text="Refresh every (e.g. 3 - 1/3 - mon - 1/3,Mon)",
        default="mon,tue,wed,thu,fri,sat,sun",
        validators=[FrequencyValidator()],
    )
    last_run = models.DateTimeField(null=True, blank=True)
    validity_days = models.IntegerField(default=365)

    tags = TaggableManager(blank=True)

    class Tenant:
        tenant_filter_field = "query__project"

    def save(
        self,
        force_insert: bool = False,
        force_update: bool = False,
        using: Optional[Any] = None,
        update_fields: Optional[Any] = None,
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
        for dataset in query.datasets.all():
            if not dataset.size:
                continue
            try:
                context = dataset.arguments
                if dataset.extra:
                    context.update(pickle.loads(dataset.extra) or {})

                title = (self.title % context) if self.title else self.title
                with profile() as perfs:
                    output = self.formatter.render(
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
                        "content_type": self.formatter.content_type,
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

    def _queue(self) -> str:
        from .celery_tasks import refresh_report

        res = refresh_report.delay(self.id)
        self.celery_task = res.id
        self.save()
        return res.id


class ReportDocumentManager(models.Manager):
    def get_queryset(self) -> models.QuerySet:
        return super().get_queryset().select_related("report")


class ReportDocument(PowerQueryModel, models.Model):
    timestamp = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=300)
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name="documents")
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    output = models.BinaryField(null=True, blank=True)
    arguments = models.JSONField(default=dict, encoder=PQJSONEncoder)
    limit_access_to = models.ManyToManyField(get_user_model(), blank=True, related_name="+")
    content_type = models.CharField(max_length=5, choices=MIMETYPES)  # type: ignore # internal mypy error
    info = models.JSONField(default={}, blank=True, null=False)
    objects = ReportDocumentManager()

    class Meta:
        unique_together = ("report", "dataset")

    class Tenant:
        tenant_filter_field = "report__query__project"

    def __str__(self) -> str:
        return self.title

    @cached_property
    def data(self) -> Any:
        return pickle.loads(self.output)

    @cached_property
    def size(self) -> int:
        return len(self.output)

    def get_absolute_url(self) -> str:
        return reverse("power_query:document", args=[self.report.pk, self.pk])
