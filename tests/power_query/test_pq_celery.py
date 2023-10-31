from typing import TYPE_CHECKING

import pytest
from unittest import mock
from unittest.mock import MagicMock

from django.conf import settings

from celery.result import EagerResult
from django_celery_beat.models import PeriodicTask

from hope_country_report.apps.power_query.celery_tasks import refresh_report, reports_refresh, run_background_query
from hope_country_report.apps.power_query.exceptions import QueryRunCanceled, QueryRunTerminated
from hope_country_report.config.celery import app
from hope_country_report.state import state

if TYPE_CHECKING:
    from typing import TypedDict

    from hope_country_report.apps.core.models import CountryOffice
    from hope_country_report.apps.hope.models import Household
    from hope_country_report.apps.power_query.models import Query, Report

    class _DATA(TypedDict):
        co1: CountryOffice
        hh1: tuple[Household, Household]


@pytest.fixture()
def data() -> "_DATA":
    from testutils.factories import CountryOfficeFactory, HouseholdFactory

    with state.set(must_tenant=False):
        co1: "CountryOffice" = CountryOfficeFactory(name="Afghanistan")

        h11: "Household" = HouseholdFactory(business_area=co1.business_area, withdrawn=True)
        h12: "Household" = HouseholdFactory(business_area=co1.business_area, withdrawn=False)
    return {"co1": co1, "hh1": (h11, h12)}


@pytest.fixture()
def query1(data: "_DATA"):
    from testutils.factories import QueryFactory, UserFactory

    yield QueryFactory(owner=UserFactory())


@pytest.fixture()
def query_exception(data: "_DATA"):
    from testutils.factories import QueryFactory, UserFactory

    yield QueryFactory(owner=UserFactory(), code="raise Exception('internal exc')")


@pytest.fixture()
def query2():
    from testutils.factories import Query, QueryFactory

    Query.objects.filter(name="Debug Query").delete()
    q = QueryFactory(
        owner=None,
        name="Debug Query",
        curr_async_result_id=None,
        code="""import time;
start=time.time()
while True:
    time.sleep(1)
    print(f"Query: {self} -  Aborted: {self.is_aborted()}")
    if time.time() > start + 10:  # max 10 secs
        break
""",
    )
    yield q
    if q.curr_async_result_id:
        with app.pool.acquire(block=True) as conn:
            conn.default_channel.client.srem(settings.CELERY_TASK_REVOKED_QUEUE, q.curr_async_result_id)


@pytest.fixture()
def report(query1: "Query"):
    from testutils.factories import ReportFactory

    return ReportFactory(name="Celery Report", query=query1, owner=query1.owner)


def test_run_background_query(settings, query1: "Query") -> None:
    settings.CELERY_TASK_ALWAYS_EAGER = True
    run_background_query.delay(query1.pk, query1.version)
    assert query1.datasets.exists()


def test_run_background_query_version_mismatch(settings, query1: "Query") -> None:
    settings.CELERY_TASK_ALWAYS_EAGER = True
    result = run_background_query.delay(query1.pk, -1)
    assert result.state == "REJECTED"


def test_run_background_query_removed(settings, query1: "Query", monkeypatch) -> None:
    from hope_country_report.apps.power_query.models import Query

    settings.CELERY_TASK_ALWAYS_EAGER = True
    with mock.patch("hope_country_report.apps.power_query.models.Query.status", Query.CANCELED):
        result: EagerResult = run_background_query.delay(query1.pk, query1.version)
        assert result.state == "IGNORED"


def test_run_background_query_canceled(settings, query1: "Query", monkeypatch) -> None:
    settings.CELERY_TASK_ALWAYS_EAGER = True
    with mock.patch("hope_country_report.apps.power_query.models.Query.execute_matrix", side_effect=QueryRunCanceled()):
        result: EagerResult = run_background_query.delay(query1.pk, query1.version)
        assert result.state == "REJECTED"


def test_run_background_query_terminate(settings, query1: "Query", monkeypatch) -> None:
    settings.CELERY_TASK_ALWAYS_EAGER = True
    with mock.patch(
        "hope_country_report.apps.power_query.models.Query.execute_matrix", side_effect=QueryRunTerminated()
    ):
        result: EagerResult = run_background_query.delay(query1.pk, query1.version)
        assert result.state == "REJECTED"


def test_refresh_report(report: "Report") -> None:
    refresh_report.delay(report.pk)
    assert report.documents.exists()


def test_celery_no_worker(db, settings, query2: "Query") -> None:
    settings.CELERY_TASK_ALWAYS_EAGER = False
    assert query2.status == "Not scheduled"
    query2.queue()
    assert query2.status == "QUEUED"
    query2.terminate()
    assert query2.status == "CANCELED"


def test_celery_reports_refresh(db, settings, report: "Report") -> None:
    settings.CELERY_TASK_ALWAYS_EAGER = True
    pt = PeriodicTask.objects.first()
    report.schedule = pt
    pt.save()

    r = MagicMock()
    r.properties = {"periodic_task_name": pt.name}
    with mock.patch("hope_country_report.apps.power_query.celery_tasks.ReportTask.request", r):
        result = reports_refresh.delay()
    assert result.state == "SUCCESS"


# @pytest.fixture(scope="session")
# def celery_config():
#     return {"broker_url": settings.CELERY_BROKER_URL, "result_backend": settings.CELERY_BROKER_URL}
#
#
# @pytest.fixture(scope="session")
# def celery_enable_logging():
#     return True
#
#
# @pytest.fixture(scope="session")
# def celery_worker_pool():
#     return "prefork"
#


@pytest.mark.django_db(transaction=True)
def test_celery_error(settings, query_exception: "Query") -> None:
    settings.CELERY_TASK_ALWAYS_EAGER = True
    query_exception.last_run = None
    result = query_exception.queue()
    assert result
    query_exception.refresh_from_db()
    assert query_exception.last_run
    assert query_exception.curr_async_result_id == result
    assert query_exception.status == "Not scheduled"
    assert query_exception.error_message


#
#
# @pytest.mark.django_db(transaction=True)
# def test_celery_async(settings, celery_worker, query_exception: "Query") -> None:
#     settings.CELERY_TASK_ALWAYS_EAGER = True
#     query_exception.last_run = None
#     result = query_exception.queue()
#     assert result
#     query_exception.refresh_from_db()
#     assert query_exception.last_run
#     assert query_exception.curr_async_result_id == result
#     assert query_exception.status == "Not scheduled"
#     assert query_exception.error_message
