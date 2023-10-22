from typing import TYPE_CHECKING

import pytest

from django.urls import reverse

from hope_country_report.state import state

if TYPE_CHECKING:
    from typing import Tuple, TypedDict

    from hope_country_report.apps.core.models import CountryOffice
    from hope_country_report.apps.hope.models import Household
    from hope_country_report.apps.power_query.models import Query, Report, ReportTemplate

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
def report(query1: "Query"):
    from testutils.factories import ReportFactory

    return ReportFactory(name="Celery Report", query=query1, owner=query1.owner)


@pytest.fixture()
def report_template():
    from testutils.factories import ReportTemplate

    return ReportTemplate.objects.first()


def test_report_list(django_app, report):
    url = reverse("power_query:report_list")
    res = django_app.get(url, user=report.owner)
    assert res


def test_report(django_app, report):
    url = reverse("power_query:report", args=[report.pk])
    res = django_app.get(url, user=report.owner)
    assert res


def test_document(django_app, report: "Report"):
    url = reverse("power_query:document", args=[report.pk, report.documents.first().pk])
    res = django_app.get(url, user=report.owner)
    assert res


def test_download(django_app, report_template: "ReportTemplate"):
    url = reverse("download-media", args=[report_template.doc.name])
    res = django_app.get(url)
    assert res
