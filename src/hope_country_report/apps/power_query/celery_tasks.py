from typing import Any, Type, TYPE_CHECKING, Union

import logging
import signal
import uuid

from django.apps import apps
from django.conf import settings
from django.core.cache import caches
from django.db import connection
from django.utils.functional import cached_property

from celery import group
from celery.contrib.abortable import AbortableTask
from celery.exceptions import Ignore, Reject
from concurrency.exceptions import RecordModifiedError
from django_celery_beat.models import PeriodicTask
from redis import StrictRedis

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
    model: "Union[Type[Query], Type[ReportConfiguration]]"
    cache = caches[getattr(settings, "CELERY_TASK_LOCK_CACHE", "default")]
    lock_expiration = 60 * 60 * 24  # 1 day
    model_name: str = ""
    abstract = True

    @cached_property
    def model(self):
        return apps.get_app_config("power_query").get_model(self.model_name)

    def after_return(self, *args, **kwargs):
        if not settings.CELERY_TASK_ALWAYS_EAGER:
            connection.close()

    def on_success(self, retval, task_id, args, kwargs):
        rds.eval(REMOVE_ONLY_IF_OWNER_SCRIPT, 1, self.lock_key, self.lock_signature)
        super().on_success(retval, task_id, args, kwargs)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        rds.eval(REMOVE_ONLY_IF_OWNER_SCRIPT, 1, self.lock_key, self.lock_signature)
        super().on_failure(exc, task_id, args, kwargs, einfo)

    @property
    def lock_key(self):
        return f"PowerQueryLock_{self.__class__.__name__}_{self.request.id}_{self.request.retries}"

    def acquire_lock(self):
        lock_acquired = bool(rds.set(self.lock_key, self.lock_signature, ex=self.lock_expiration, nx=True))
        logger.debug("Acquiring %s key %s", self.lock_key, "succeed" if lock_acquired else "failed")
        return lock_acquired

    def __call__(self, *args, **kwargs):
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
        if query.status == Query.CANCELED:
            raise Ignore()

        def trap(sig, frame):
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
    except (Ignore, Reject):
        raise
    except BaseException as e:
        logger.exception(e)
        raise


@app.task(bind=True, default_retry_delay=60, max_retries=3, base=ReportTask)
@sentry_tags
def refresh_report(self: PowerQueryTask, id: int, version: int = 0) -> "ReportResult":
    from hope_country_report.apps.power_query.models import ReportConfiguration

    result: "ReportResult" = []
    try:
        report: ReportConfiguration = ReportConfiguration.objects.get(id=id)
        result = report.execute(run_query=True)
    except Exception as e:
        logger.exception(e)
    return result


@app.task(bind=True, default_retry_delay=60, max_retries=3, base=ReportTask)
@sentry_tags
def reports_refresh(self: AbortableTask, **kwargs) -> Any:
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
