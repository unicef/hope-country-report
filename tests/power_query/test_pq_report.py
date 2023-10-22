from typing import TYPE_CHECKING

import pytest

from django.conf import settings

from hope_country_report.config.celery import app

if TYPE_CHECKING:
    from hope_country_report.apps.power_query.models import Query, Report


@pytest.fixture()
def query2():
    from testutils.factories import Query, QueryFactory

    Query.objects.filter(name="Debug Query").delete()
    q = QueryFactory(
        owner=None,
        name="Debug Query",
        curr_async_result_id=None,
        code="""result=[1,2,3,4]""",
    )
    yield q
    if q.curr_async_result_id:
        with app.pool.acquire(block=True) as conn:
            conn.default_channel.client.srem(settings.CELERY_TASK_REVOKED_QUEUE, q.curr_async_result_id)


@pytest.fixture()
def report(query2: "Query"):
    from testutils.factories import ReportFactory

    return ReportFactory(name="Celery Report", query=query2, owner=query2.owner)


def test_celery_no_worker(db, settings, report: "Report") -> None:
    settings.CELERY_TASK_ALWAYS_EAGER = False
    assert report.status == "Not scheduled"
    report.queue()
    assert report.status == "QUEUED"
    report.terminate()
    assert report.status == "CANCELED"
