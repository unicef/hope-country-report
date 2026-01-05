import uuid
from typing import TYPE_CHECKING
from unittest import mock
from unittest.mock import MagicMock, PropertyMock

import pytest
from celery import states
from celery.result import EagerResult
from django.conf import settings
from django_celery_beat.models import PeriodicTask

from hope_country_report.apps.power_query.celery_tasks import refresh_report, reports_refresh, run_background_query
from hope_country_report.apps.power_query.exceptions import QueryRunCanceled, QueryRunTerminated
from hope_country_report.apps.power_query.models import Query, ReportConfiguration
from hope_country_report.config.celery import app
from hope_country_report.state import state

if TYPE_CHECKING:
    from typing import TypedDict

    from hope_country_report.apps.core.models import CountryOffice
    from hope_country_report.apps.hope.models import Household

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
def report(query1: Query):
    from testutils.factories import ReportConfigurationFactory

    return ReportConfigurationFactory(name="Celery Report", query=query1, owner=query1.owner)


@pytest.fixture()
def periodic_task_fixture(report: "ReportConfiguration"):
    from django_celery_beat.models import IntervalSchedule, PeriodicTask

    schedule, _ = IntervalSchedule.objects.get_or_create(
        every=1,
        period=IntervalSchedule.DAYS,
    )
    pt_name = f"test_reports_schedule_{uuid.uuid4().hex}"
    task_path = "hope_country_report.apps.power_query.celery_tasks.reports_refresh"
    pt = PeriodicTask.objects.create(interval=schedule, name=pt_name, task=task_path)
    report.schedule = pt
    report.save()

    yield pt

    if ReportConfiguration.objects.filter(pk=report.pk).exists():
        report_obj = ReportConfiguration.objects.get(pk=report.pk)
        report_obj.schedule = None
        report_obj.save()
    if PeriodicTask.objects.filter(pk=pt.pk).exists():
        PeriodicTask.objects.get(pk=pt.pk).delete()


def test_run_background_query(settings, query1: Query) -> None:
    settings.CELERY_TASK_ALWAYS_EAGER = True
    run_background_query.delay(query1.pk, query1.version)
    assert query1.datasets.exists()


def test_run_background_query_version_mismatch(settings, query1: Query) -> None:
    settings.CELERY_TASK_ALWAYS_EAGER = True
    result: EagerResult = run_background_query.delay(query1.pk, -1)
    assert result.state == states.REJECTED


def test_run_background_query_removed(settings, query1: Query) -> None:
    from unittest.mock import PropertyMock

    settings.CELERY_TASK_ALWAYS_EAGER = True
    with mock.patch(
        "hope_country_report.apps.power_query.models.Query.task_status",
        new_callable=PropertyMock,
        return_value=states.REVOKED,
    ):
        result: EagerResult = run_background_query.delay(query1.pk, query1.version)
        assert result.state == "SUCCESS"


def test_run_background_query_canceled(settings, query1: Query, monkeypatch) -> None:
    settings.CELERY_TASK_ALWAYS_EAGER = True
    with mock.patch("hope_country_report.apps.power_query.models.Query.execute_matrix", side_effect=QueryRunCanceled()):
        result: EagerResult = run_background_query.delay(query1.pk, query1.version)
        assert result.state == "REJECTED"


def test_run_background_query_terminate(settings, query1: Query, monkeypatch) -> None:
    settings.CELERY_TASK_ALWAYS_EAGER = True
    with mock.patch(
        "hope_country_report.apps.power_query.models.Query.execute_matrix", side_effect=QueryRunTerminated()
    ):
        result: EagerResult = run_background_query.delay(query1.pk, query1.version)
        assert result.state == "REJECTED"


def test_refresh_report(report: "ReportConfiguration") -> None:
    refresh_report.delay(report.pk)
    assert report.documents.exists()


def test_celery_reports_refresh(
    db, settings, report: "ReportConfiguration", periodic_task_fixture: PeriodicTask
) -> None:
    settings.CELERY_TASK_ALWAYS_EAGER = True

    pt = periodic_task_fixture

    mock_task_self_request = MagicMock(name="mock_task_self_request")
    mock_task_self_request.periodic_task_name = pt.name
    mock_task_self_request.id = f"test_task_id_{uuid.uuid4().hex}"

    with mock.patch("celery.app.task.Task.request", new_callable=PropertyMock, return_value=mock_task_self_request):
        result_from_delay = reports_refresh.delay()

    assert isinstance(result_from_delay, EagerResult)
    assert result_from_delay.successful()
    report.refresh_from_db()
    assert report.documents.exists()


@pytest.mark.django_db
def test_celery_error(settings, query_exception: Query) -> None:
    settings.CELERY_TASK_ALWAYS_EAGER = True
    settings.CELERY_TASK_STORE_EAGER_RESULT = True
    query_exception.last_run = None
    query_exception.error_message = None
    query_exception.sentry_error_id = None
    query_exception.save()

    query_exception.queue()

    query_exception.refresh_from_db()

    if "async_result" in query_exception.__dict__:
        query_exception.__dict__.pop("async_result", None)

    assert query_exception.error_message == "internal exc"
    assert query_exception.sentry_error_id
    assert query_exception.effective_status == Query.FAILURE
