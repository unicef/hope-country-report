from typing import Any, TYPE_CHECKING

import logging
import signal
import uuid

from django.apps import apps
from django.conf import settings
from django.core.cache import caches
from django.db import connection
from django.db.models import Model
from django.utils.functional import cached_property

from billiard.einfo import ExceptionInfo
from celery import group
from celery.contrib.abortable import AbortableTask
from celery.exceptions import Ignore, Reject, Retry
from concurrency.exceptions import RecordModifiedError
from django_celery_beat.models import PeriodicTask
from redis import StrictRedis
from sentry_sdk import capture_exception

from ...config.celery import app
from .exceptions import QueryRunCanceled, QueryRunTerminated
from .utils import sentry_tags

if TYPE_CHECKING:
    from .models import Query, QueryMatrixResult, ReportConfiguration, ReportResult

logger = logging.getLogger(__name__)

REMOVE_ONLY_IF_OWNER_SCRIPT = """
if redis.call("get",KEYS[1]) == ARGV[1] then
    return redis.call("del",KEYS[1])
else
    return 0
end
"""
rds = StrictRedis(settings.REDIS_URL, decode_responses=True, charset="utf-8")


class AbstractPowerQueryTask(AbortableTask):
    model: "type[Query] | type[ReportConfiguration]"
    cache = caches[getattr(settings, "CELERY_TASK_LOCK_CACHE", "default")]
    lock_expiration = 60 * 60 * 24  # 1 day
    model_name: str = ""
    abstract = True

    @cached_property
    def model(self) -> type[Model]:
        return apps.get_app_config("power_query").get_model(self.model_name)

    def after_return(self, *args: Any, **kwargs: Any) -> None:
        if not settings.CELERY_TASK_ALWAYS_EAGER:
            connection.close()

    def on_success(self, retval: Any, task_id: str, args: tuple, kwargs: dict[str, str]) -> None:
        rds.eval(REMOVE_ONLY_IF_OWNER_SCRIPT, 1, self.lock_key, self.lock_signature)
        super().on_success(retval, task_id, args, kwargs)

    def on_failure(
        self, exc: Exception, task_id: str, args: tuple, kwargs: dict[str, str], einfo: ExceptionInfo
    ) -> None:
        try:
            obj_id = args[0]
            instance = self.model.objects.filter(pk=obj_id).first()
            if instance:
                instance.error_message = str(exc)
                sentry_id = getattr(einfo, "sentry_event_id", None) or capture_exception(exc)
                instance.sentry_error_id = str(sentry_id) if sentry_id else None
                instance.save(update_fields=["error_message", "sentry_error_id"])
        except Exception as e:
            logger.error(f"Failed to save error details for task {task_id} on failure: {e}")

        rds.eval(REMOVE_ONLY_IF_OWNER_SCRIPT, 1, self.lock_key, self.lock_signature)
        super().on_failure(exc, task_id, args, kwargs, einfo)

    @property
    def lock_key(self) -> str:
        return f"PowerQueryLock_{self.__class__.__name__}_{self.request.id}_{self.request.retries}"

    def acquire_lock(self) -> bool:
        lock_acquired = bool(rds.set(self.lock_key, self.lock_signature, ex=self.lock_expiration, nx=True))
        logger.debug("Acquiring %s key %s", self.lock_key, "succeed" if lock_acquired else "failed")
        return lock_acquired

    def __call__(self, *args: tuple, **kwargs: dict[str, str]) -> Any:
        self.lock_signature = str(uuid.uuid4())
        if self.acquire_lock():
            logger.debug("Task %s execution with lock started", self.request.id)
            return super().__call__(*args, **kwargs)
        logger.warning("Task %s skipped due lock detection", self.request.id)


class PowerQueryTask(AbstractPowerQueryTask):
    model_name = "Query"


class ReportTask(AbstractPowerQueryTask):
    model_name = "Report"


@app.task(bind=True, base=PowerQueryTask)
@sentry_tags
def run_background_query(self: PowerQueryTask, query_id: int, version: int) -> "QueryMatrixResult":
    from hope_country_report.apps.power_query.models import Query

    query = None
    try:
        query = Query.objects.get(pk=query_id)
        if query.version != version:
            raise RecordModifiedError(target=query)
        query.error_message = None
        query.sentry_error_id = None
        query.save(update_fields=["error_message", "sentry_error_id"])

        def trap(sig: Any, frame: Any):
            raise QueryRunTerminated

        for sig in ("TERM", "HUP", "INT", "USR1"):
            signal.signal(getattr(signal, "SIG" + sig), trap)

        res = query.execute_matrix(running_task=self)
        return res
    except QueryRunTerminated as e:
        raise Reject(e, requeue=False)
    except QueryRunCanceled as e:
        if query and query.curr_async_result_id:
            with app.pool.acquire(block=True) as conn:
                conn.default_channel.client.srem(settings.CELERY_TASK_REVOKED_QUEUE, query.curr_async_result_id)
            app.control.revoke(query.curr_async_result_id)
        raise Reject(e, requeue=False)
    except RecordModifiedError as e:
        raise Reject(e, requeue=False)
    except (Ignore, Reject, Retry):
        raise
    except Exception as e:
        logger.exception(f"Unhandled exception in run_background_query for query {query_id}: {e}")
        raise


@app.task(bind=True, default_retry_delay=60, max_retries=3, base=ReportTask)
@sentry_tags
def refresh_report(self: PowerQueryTask, id: int, version: int = 0) -> "ReportResult":
    from hope_country_report.apps.power_query.models import ReportConfiguration

    result: "ReportResult" = []
    report = None
    try:
        report = ReportConfiguration.objects.get(id=id)
        if version and report.version != version:
            raise RecordModifiedError(target=report)

        report.error_message = None
        report.sentry_error_id = None
        report.save(update_fields=["error_message", "sentry_error_id"])

        result = report.execute(run_query=True)
    except RecordModifiedError as e:
        raise Reject(e, requeue=False)
    except (Ignore, Reject, Retry):
        raise
    except Exception as e:
        logger.exception(f"Unhandled exception in refresh_report for report {id}: {e}")
        if report:
            try:
                report.error_message = str(e)
                report.sentry_error_id = str(capture_exception(e))
                report.save(update_fields=["error_message", "sentry_error_id"])
            except Exception as save_e:
                logger.error(f"Failed to save error details for report {id} on exception: {save_e}")
        raise
    return result


@app.task(bind=True, default_retry_delay=60, max_retries=3, base=ReportTask)
@sentry_tags
def reports_refresh(self: AbortableTask, **kwargs: dict[str, Any]) -> Any:
    from hope_country_report.apps.power_query.models import ReportConfiguration

    report: ReportConfiguration
    result = {}
    if periodic_task_name := (getattr(self.request, "properties", {}) or {}).get("periodic_task_name"):
        periodic_task = PeriodicTask.objects.get(name=periodic_task_name)
        grp = []
        for report in periodic_task.reports.filter(active=True):
            grp.append(refresh_report.subtask([report.pk, report.version]))

        if grp:
            job = group(grp)
            result = job.apply_async()

        return result
