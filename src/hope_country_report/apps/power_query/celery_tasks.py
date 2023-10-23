from typing import Any, Dict, Tuple, Type, TYPE_CHECKING, Union

import logging
import signal

from django.conf import settings

from celery.contrib.abortable import AbortableTask
from celery.exceptions import Ignore, Reject
from concurrency.exceptions import RecordModifiedError

from ...config.celery import app
from .exceptions import QueryRunCanceled, QueryRunTerminated
from .models import Query, Report
from .utils import sentry_tags

if TYPE_CHECKING:
    from .models import QueryMatrixResult, ReportResult

logger = logging.getLogger(__name__)


class AbstractPowerQueryTask(AbortableTask):
    model: "Union[Type[Query], Type[Report]]"

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        super().after_return(status, retval, task_id, args, kwargs, einfo)

    def on_success(self, retval: Any, task_id: str, args: Tuple[Any], kwargs: Dict[str, Any]) -> None:
        instance = self.model.objects.filter(id=args[0]).first()
        instance.last_async_result_id = task_id
        instance.curr_async_result_id = None
        instance.save()


class PowerQueryTask(AbstractPowerQueryTask):
    model = Query


class ReportTask(AbstractPowerQueryTask):
    model = Report


@app.task(bind=True, base=PowerQueryTask)
@sentry_tags
def run_background_query(self: PowerQueryTask, query_id: int, version: int) -> "QueryMatrixResult":
    try:
        query: Query = Query.objects.get(pk=query_id)
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
    except QueryRunCanceled as e:
        with app.pool.acquire(block=True) as conn:
            conn.default_channel.client.srem(settings.CELERY_TASK_REVOKED_QUEUE, self.request.id)
        app.control.revoke(self.request.id)
        raise Reject(e, requeue=False)
    except RecordModifiedError as e:
        raise Reject(e, requeue=False)
    except QueryRunTerminated:
        raise
    except BaseException as e:
        logger.exception(e)
        raise


@app.task(bind=True, default_retry_delay=60, max_retries=3, base=ReportTask)
@sentry_tags
def refresh_report(self: PowerQueryTask, id: int, version: int = 0) -> "ReportResult":
    result: "ReportResult" = []
    try:
        report: Report = Report.objects.get(id=id)
        result = report.execute(run_query=True)
    except Exception as e:
        logger.exception(e)
    return result


@app.task(bind=True, default_retry_delay=60, max_retries=3, base=ReportTask)
@sentry_tags
def period_task_manager(self: Any) -> Any:
    results: Any = []
    # report: Report
    # try:
    #     for report in Report.objects.select_related("owner", "query", "formatter").filter(
    #         active=True, frequence__isnull=False
    #     ):
    #         if should_run(report.frequence):
    #             ret = report.queue()
    #             results.append(ret)
    #         else:
    #             results.append([report.pk, "skip"])
    # except BaseException as e:
    #     logger.exception(e)
    #     raise self.retry(exc=e)
    return results
