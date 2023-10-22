from typing import TYPE_CHECKING

import pytest

from django.conf import settings

from hope_country_report.apps.power_query.celery_tasks import refresh_report, run_background_query
from hope_country_report.config.celery import app
from hope_country_report.state import state

if TYPE_CHECKING:
    from typing import Tuple, TypedDict

    from hope_country_report.apps.core.models import CountryOffice
    from hope_country_report.apps.hope.models import Household
    from hope_country_report.apps.power_query.models import Query, Report

    _DATA = TypedDict(
        "_DATA",
        {
            "co1": CountryOffice,
            "hh1": Tuple[Household, Household],
        },
    )


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
    if time.time() > start + 5:  # max 5 secs
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


@pytest.fixture(scope="session")
def celery_config():
    return {"broker_url": "redis://", "result_backend": "redis://"}


def test_run_background_query(settings, query1: "Query") -> None:
    settings.CELERY_TASK_ALWAYS_EAGER = True
    run_background_query.delay(query1.pk, query1.version)
    assert query1.datasets.exists()


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


# @pytest.mark.celery()
# def test_celery_worker(settings, transactional_db, query2: "Query") -> None:
#     settings.CELERY_TASK_ALWAYS_EAGER = False
#     assert query2.status == "Not scheduled"
#     query2.queue()
#     assert query2.status == "STARTED"
#     query2.terminate()
#     assert query2.status == "CANCELED"


# @pytest.fixture(scope='session')
# def celery_worker_parameters():
#     return {
#         'result_backend': 'redis://',
#         'broker_url': 'redis://127.0.0.1/8',
#     }
#
# @pytest.fixture(scope='session')
# def celery_config():
#     return {
#         'result_backend': 'redis://',
#         'broker_url': 'redis://127.0.0.1/8',
#     }
#


# @pytest.fixture
# def db_access_without_rollback_and_truncate(request, django_db_setup, django_db_blocker):
#     django_db_blocker.unblock()
#     request.addfinalizer(django_db_blocker.restore)
#
#
# @pytest.mark.celery()
# @pytest.mark.django_db(transaction=True)
# def test_celery_query(settings, celery_app, celery_worker, query2) -> None:
#     celery_app.control.purge()
#     settings.CELERY_TASK_ALWAYS_EAGER = False
#     query2.queue()
#     time.sleep(1)
#     assert query2.status == 'STARTED'
