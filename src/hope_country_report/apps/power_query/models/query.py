from typing import Iterable, TYPE_CHECKING

import hashlib
import logging
import tempfile
import types

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.files.base import ContentFile
from django.db import models, transaction
from django.db.models import JSONField, Q
from django.utils import timezone

from sentry_sdk import capture_exception, configure_scope

from hope_country_report.apps.core.models import CountryOffice
from hope_country_report.state import state
from hope_country_report.utils.perf import profile

from ..celery_tasks import PowerQueryTask
from ..exceptions import QueryRunCanceled
from ..json import PQJSONEncoder
from ..utils import dict_hash, to_dataset
from ._base import AdminReversable, CeleryEnabled, PowerQueryModel
from .arguments import Parametrizer

if TYPE_CHECKING:
    from typing import Any

    from django.db.models import QuerySet

    from hope_country_report.types.django import AnyModel
    from hope_country_report.types.pq import QueryMatrixResult

    from .dataset import Dataset

logger = logging.getLogger(__name__)


class Query(CeleryEnabled, PowerQueryModel, AdminReversable, models.Model):
    country_office = models.ForeignKey(CountryOffice, on_delete=models.CASCADE, blank=True, null=True)

    datasets: "QuerySet[Dataset]"
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    parent = models.ForeignKey("self", blank=True, null=True, on_delete=models.CASCADE)
    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, blank=True, null=True, related_name="queries")
    target = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    code = models.TextField(default="result=conn.all()", blank=True, null=True)
    info = JSONField(default=dict, blank=True, encoder=PQJSONEncoder)
    parametrizer = models.ForeignKey(Parametrizer, on_delete=models.CASCADE, blank=True, null=True)
    active = models.BooleanField(default=True)

    celery_task_name = "run_background_query"

    def __str__(self) -> str:
        if self.abstract:
            return f"[ABSTRACT] {self.name}"
        if self.parent:
            return f"{self.name} ({self.parent.name})"
        return self.name

    class Meta:
        verbose_name_plural = "Queries"
        ordering = ("name",)

        constraints = [
            models.CheckConstraint(
                condition=Q(
                    parent__isnull=False, country_office__isnull=False, code__isnull=True, target__isnull=True
                )  # implementation
                | Q(parent__isnull=True, code__isnull=False, target__isnull=False),  # standard or abstract with code
                name="valid_query",
            )
        ]

    class Tenant:
        tenant_filter_field = "country_office"

    @property
    def abstract(self):
        return bool(not self.parent and self.code)

    @property
    def children(self):
        return Query.objects.filter(parent=self)

    def full_clean(
        self, exclude: Iterable[str] | None = ..., validate_unique: bool = ..., validate_constraints: bool = ...
    ) -> None:
        if self.code == "":
            self.code = None
        super().full_clean(exclude, validate_unique, validate_constraints)

    def _invoke(self, query_id: int, arguments: "dict[str, Any]") -> "tuple[Any, Any]":
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
        args = self.get_args()
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
                    except Exception as e:
                        logger.exception(e)
                        err = capture_exception(e)
                        results["sentry_error_id"] = str(err)
                        results["error_message"] = str(e)

                self.datasets.exclude(pk__in=[dpk for dpk in results.values() if isinstance(dpk, int)]).delete()
        return results

    def run(
        self,
        persist: bool = False,
        arguments: "dict[str,Any]|None" = None,
        use_existing: bool = False,
        preview: bool = False,
        running_task: "PowerQueryTask|None" = None,
        **kwargs: "dict[str, Any]",
    ) -> "tuple[Dataset, dict[str,Any]]":
        from .dataset import Dataset

        model = self.parent.target.model_class() if self.parent else self.target.model_class()
        connections: "dict[str, QuerySet[AnyModel]]" = {}
        return_value: "tuple[Dataset, dict[str, Any]]"
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
                fp = tempfile.TemporaryFile()
                locals_ = {
                    "conn": model._default_manager.using(settings.POWER_QUERY_DB_ALIAS),
                    "self": self,
                    "args": arguments,
                    "arguments": arguments,
                    "to_dataset": to_dataset,
                    "invoke": self._invoke,
                    "debug": lambda *a: debug.append((timezone.now().strftime("%H:%M:%S"), *a)),
                    "task": running_task,
                    "fp": fp,
                    **kwargs,
                    **connections,
                }
                signature = dict_hash({"query": self.pk, **(arguments if arguments else {})})
                if not preview and use_existing and (ds := Dataset.objects.filter(query=self, hash=signature).first()):
                    return_value = ds, ds.extra
                else:
                    with state.set(preview=preview, tenant=self.country_office):
                        try:
                            code = self.get_code()
                            exec(code, globals(), locals_)
                            result = locals_.get("result")
                            extra = locals_.get("extra")
                        except Exception:
                            self.info = {
                                "debug": debug,
                            }
                            self.save()
                            raise
                        info = {
                            "type": type(result).__name__,
                            "arguments": arguments,
                            "perfs": perfs,
                            "debug": debug,
                            "extra": extra,
                        }
                        h = hashlib.md5(str(arguments).encode()).hexdigest()

                        defaults = {
                            "size": len(result) if result else 0,
                            "info": info,
                            "last_run": timezone.now(),
                            "file": ContentFile(Dataset.marshall(result), name=f"{self.pk}_{h}.pkl"),
                            # "extra": pickle.dumps(extra),
                        }
                        if persist:
                            dataset, __ = Dataset.objects.update_or_create(
                                query=self, hash=signature, defaults=defaults
                            )
                        else:
                            dataset = Dataset(query=self, hash=signature, **defaults)

                        return_value = dataset, extra
        except Exception:
            raise
        return return_value

    def get_code(self):
        return self.parent.code if self.parent else self.code

    def get_args(self):
        args = [{}]
        if self.parametrizer:
            args = self.parametrizer.get_matrix()
        elif self.parent and self.parent.parametrizer:
            args = self.parent.parametrizer.get_matrix()
        return args
