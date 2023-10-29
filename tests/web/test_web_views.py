from typing import TYPE_CHECKING

import pytest

from django.urls import reverse

from hope_country_report.state import state

if TYPE_CHECKING:
    from typing import TypedDict

    from hope_country_report.apps.core.models import CountryOffice
    from hope_country_report.apps.hope.models import Household
    from hope_country_report.apps.power_query.models import Query, Report, ReportTemplate

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
def report(query1: "Query"):
    from testutils.factories import ReportFactory

    return ReportFactory(name="Celery Report", query=query1, owner=query1.owner)


@pytest.fixture()
def report_template():
    from testutils.factories import ReportTemplate

    return ReportTemplate.objects.first()


def test_index(django_app, report):
    res = django_app.get("/", user=report.owner)
    assert res.status_code == 200


def test_report_list(django_app, report):
    url = reverse("office-reports", args=[report.country_office.slug])
    res = django_app.get(url, user=report.owner)
    assert res.status_code == 200


def test_user_list(django_app, report):
    url = reverse("office-users", args=[report.country_office.slug])
    res = django_app.get(url, user=report.owner)
    assert res.status_code == 200


def test_dashboard_list(django_app, report):
    url = reverse("office-pages", args=[report.country_office.slug])
    res = django_app.get(url, user=report.owner)
    assert res.status_code == 200


def test_report(django_app, report):
    url = reverse("office-report", args=[report.country_office.slug, report.pk])
    res = django_app.get(url, user=report.owner)
    assert res.status_code == 200


def test_document(django_app, report: "Report"):
    url = reverse("office-doc-display", args=[report.country_office.slug, report.pk, report.documents.first().pk])
    res = django_app.get(url, user=report.owner)
    assert res.status_code == 200


def test_download(django_app, report: "Report"):
    url = reverse("office-doc-download", args=[report.country_office.slug, report.pk, report.documents.first().pk])
    res = django_app.get(url, user=report.owner)
    assert res.status_code == 200


def test_user_profile(django_app, report: "Report"):
    url = reverse("office-index", args=[report.country_office.slug])
    res = django_app.get(url, user=report.owner)
    res = res.click(href="/profile/")
    res.forms["user-profile"].language = "es"
    res = res.forms["user-profile"].submit()
    assert res.status_code == 302
    report.owner.refresh_from_db()
    assert report.owner.language == "es"


def test_download_media(django_app, report_template: "ReportTemplate", user):
    url = reverse("download-media", args=[report_template.doc.path])
    res = django_app.get(url, user=user)
    assert res.headers["Content-Type"] == "application/force-download"


def test_download_media_requires_login(django_app, report_template: "ReportTemplate", user):
    url = reverse("download-media", args=[report_template.doc.path])
    res = django_app.get(url)
    assert res.status_code == 302


def test_download_media_handle_missing(django_app, user):
    url = reverse("download-media", args=["missing-file.zap"])
    res = django_app.get(url, user=user, expect_errors=True)
    assert res.status_code == 404
