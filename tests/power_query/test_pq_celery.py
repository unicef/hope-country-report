from typing import TYPE_CHECKING

import pytest

from hope_country_report.apps.power_query.celery_tasks import refresh_report, refresh_reports, run_background_query
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
def data(reporters) -> "_DATA":
    from testutils.factories import CountryOfficeFactory, HouseholdFactory

    with state.set(must_tenant=False):
        co1: "CountryOffice" = CountryOfficeFactory(name="Afghanistan")

        h11: "Household" = HouseholdFactory(business_area=co1.business_area, withdrawn=True)
        h12: "Household" = HouseholdFactory(business_area=co1.business_area, withdrawn=False)
    return {"co1": co1, "hh1": (h11, h12)}


@pytest.fixture()
def query1(data: "_DATA"):
    from testutils.factories import QueryFactory, UserFactory

    return QueryFactory(owner=UserFactory())


@pytest.fixture()
def report(query1: "Query"):
    from testutils.factories import ReportFactory

    return ReportFactory(name="Celery Report", query=query1, owner=query1.owner)


def test_run_background_query(query1: "Query") -> None:
    run_background_query.delay(query1.pk)
    assert query1.datasets.exists()


def test_refresh_reports(report: "Report") -> None:
    assert report.query.owner
    refresh_reports.delay()
    assert report.documents.exists()


def test_refresh_report(report: "Report") -> None:
    refresh_report.delay(report.pk)
    assert report.documents.exists()
