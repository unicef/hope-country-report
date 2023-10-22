from typing import Any, Dict, Tuple, Type, TYPE_CHECKING, Union

import logging
import signal

from django.conf import settings

from billiard.einfo import ExceptionInfo
from celery.contrib.abortable import AbortableTask
from celery.exceptions import Ignore, Reject
from concurrency.exceptions import RecordModifiedError

from ...config.celery import app
from .exceptions import PowerQueryError, QueryRunCanceled, QueryRunError, QueryRunTerminated
from .models import Query, Report
from .utils import sentry_tags

if TYPE_CHECKING:
    from .models import QueryMatrixResult, ReportResult

logger = logging.getLogger(__name__)


class AbstractPowerQueryTask(AbortableTask):
    model: "Union[Type[Query], Type[Report]]"

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        print(f"AAAAAAAAAA {status} {retval} {type(retval)} {isinstance(retval, PowerQueryError)}")
        # print(f"src/hope_country_report/apps/power_query/celery_tasks.py: 2222 {kwargs}")
        if isinstance(retval, QueryRunCanceled):
            print("QueryRunCanceled")
        elif isinstance(retval, QueryRunTerminated):
            print("QueryRunTerminated")
            self.update_state(state="INTERRUPTED")
        elif isinstance(retval, QueryRunError):
            print("QueryRunError")
        elif isinstance(retval, PowerQueryError):
            print("PowerQueryError")
        elif isinstance(retval, dict):
            print("dict")
        else:
            print(f"{retval} {type(retval)}")
        super().after_return(status, retval, task_id, args, kwargs, einfo)

    def on_success(self, retval: Any, task_id: str, args: Tuple[Any], kwargs: Dict[str, Any]) -> None:
        """
        retval (Any): The return value of the task.
        task_id (str): Unique id of the executed task.
        args (Tuple): Original arguments for the executed task.
        kwargs (Dict): Original keyword arguments for the executed task.
        """
        instance = self.model.objects.filter(id=args[0]).first()
        instance.last_async_result_id = task_id
        instance.curr_async_result_id = None
        instance.save()

    def on_failure(
        self,
        exc: Exception,
        task_id: str,
        args: Tuple[Any],
        kwargs: Dict[str, Any],
        einfo: ExceptionInfo,
    ) -> None:
        """
        exc (Exception): The exception raised by the task.
        task_id (str): Unique id of the failed task.
        args (Tuple): Original arguments for the task that failed.
        kwargs (Dict): Original keyword arguments for the task that failed.
        einfo (~billiard.einfo.ExceptionInfo): Exception information.
        """
        print(f"ON_FAILURE {exc}")
        # print(f"src/hope_country_report/apps/power_query/celery_tasks.py: 51 {task_id}")
        # print(f"src/hope_country_report/apps/power_query/celery_tasks.py: 51 {args}")
        # # print(f"src/hope_country_report/apps/power_query/celery_tasks.py: 51 {einfo}")
        # instance = self.model.objects.filter(id=args[0]).first()
        # if instance:
        #     sid = capture_exception(exc)
        #     q.sentry_error_id = sid
        #     q.error_message = str(exc)
        #     q.save()


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
        print(f"src/hope_country_report/apps/power_query/celery_tasks.py: 122: 333 {e.__class__.__name__}:{e}")
        logger.exception(e)
        raise


@app.task(bind=True, default_retry_delay=60, max_retries=3, base=ReportTask)
@sentry_tags
def refresh_report(self: PowerQueryTask, id: int, version: int = 0) -> "ReportResult":
    result: "ReportResult" = []
    try:
        report: Report = Report.objects.get(id=id)
        result = report.execute(run_query=True)
    except Report.DoesNotExist as e:
        logger.exception(e)
    except Exception as e:
        logger.exception(e)
        raise self.retry(exc=e)
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
