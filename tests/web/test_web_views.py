from typing import TYPE_CHECKING

import pytest

from django.urls import reverse

from testutils.perms import user_grant_permissions

from hope_country_report.state import state

if TYPE_CHECKING:
    from typing import TypedDict

    from hope_country_report.apps.core.models import CountryOffice, User
    from hope_country_report.apps.hope.models import Household
    from hope_country_report.apps.power_query.models import Query, ReportConfiguration, ReportDocument, ReportTemplate

    class _DATA(TypedDict):
        co1: CountryOffice
        hh1: tuple[Household, Household]


# @pytest.fixture()
# def afg_user(user, afghanistan):
#     grant = user_grant_permissions(user, [], afghanistan)
#     grant.start()
#     yield user
#     grant.stop()
#


@pytest.fixture()
def data(afghanistan) -> "_DATA":
    from testutils.factories import HouseholdFactory

    with state.set(must_tenant=False):
        h11: "Household" = HouseholdFactory(business_area=afghanistan.business_area, withdrawn=True)
        h12: "Household" = HouseholdFactory(business_area=afghanistan.business_area, withdrawn=False)
    return {"co1": afghanistan, "hh1": (h11, h12)}


@pytest.fixture()
def query1(afg_user, afghanistan, data: "_DATA"):
    from testutils.factories import QueryFactory

    yield QueryFactory(country_office=afghanistan, owner=afg_user)


@pytest.fixture()
def report_configuration(query1: "Query"):
    from testutils.factories import ReportConfigurationFactory

    return ReportConfigurationFactory(
        country_office=query1.country_office, query=query1, owner=query1.owner, compress=False
    )


@pytest.fixture()
def report_document(report_configuration: "ReportConfiguration"):
    report_configuration.execute(True)
    return report_configuration.documents.all()[0]


@pytest.fixture()
def report_template():
    from testutils.factories import ReportTemplate

    return ReportTemplate.objects.first()


def test_index(django_app, report_configuration):
    res = django_app.get("/", user=report_configuration.owner)
    assert res.status_code == 302


def test_select_tenant(django_app, report_configuration):
    res = django_app.get(reverse("select-tenant"), user=report_configuration.owner)
    res.forms["select-tenant"]["tenant"] = report_configuration.country_office.pk
    res = res.forms["select-tenant"].submit()
    assert res.status_code == 302


def test_user_list(django_app, report_configuration):
    url = reverse("office-users", args=[report_configuration.country_office.slug])
    res = django_app.get(url, user=report_configuration.owner)
    assert res.status_code == 200


def test_dashboard_list(django_app, report_configuration: "ReportConfiguration"):
    url = reverse("office-pages", args=[report_configuration.country_office.slug])
    res = django_app.get(url, user=report_configuration.owner)
    assert res.status_code == 200


def test_report_list(django_app, report_configuration: "ReportConfiguration"):
    user: "User" = report_configuration.owner
    url = reverse("office-config-list", args=[report_configuration.country_office.slug])
    with user_grant_permissions(user, "power_query.view_reportconfiguration"):
        with state.activate_tenant(report_configuration.country_office):
            assert state.tenant == report_configuration.country_office
            assert state.tenant_cookie == report_configuration.country_office.slug
            res = django_app.get(url, user=user)
    assert res.status_code == 200


def test_report(django_app, report_document: "ReportDocument"):
    config: "ReportConfiguration" = report_document.report
    user: "User" = config.owner
    url = reverse("office-config", args=[config.country_office.slug, config.pk])
    with user_grant_permissions(user, ["power_query.view_reportconfiguration"]):
        res = django_app.get(url, user=user)
    assert res.status_code == 200


def test_document_list(django_app, report_document: "ReportDocument"):
    config: "ReportConfiguration" = report_document.report
    user: "User" = config.owner
    url = reverse("office-doc-list", args=[config.country_office.slug])
    with user_grant_permissions(user, "power_query.view_reportdocument"):
        res = django_app.get(url, user=user)
    assert res.status_code == 200


def test_document(django_app, admin_user, report_document: "ReportDocument"):
    config: "ReportConfiguration" = report_document.report
    user: "User" = config.owner
    url = reverse("office-doc", args=[config.country_office.slug, report_document.pk])
    with user_grant_permissions(user, ["power_query.view_reportdocument"]):
        res = django_app.get(url, user=user)
    assert res.status_code == 200, f"{url}: {res.status_code} != 200"


def test_document_display(django_app, report_document):
    config: "ReportConfiguration" = report_document.report
    user: "User" = config.owner
    url = reverse("office-doc-display", args=[config.country_office.slug, config.documents.first().pk])
    with user_grant_permissions(config.owner, ["power_query.view_reportconfiguration"]):
        res = django_app.get(url, user=user)
    assert res.status_code == 200


def test_document_download(django_app, report_document):
    config: "ReportConfiguration" = report_document.report
    user: "User" = config.owner
    with user_grant_permissions(user, ["power_query.download_reportdocument"], config.country_office):
        url = reverse("office-doc-download", args=[config.country_office.slug, config.documents.first().pk])
        res = django_app.get(url, user=user)
    assert res.status_code == 200, res.headers["Location"]


def test_user_profile(django_app, afghanistan, afg_user):
    url = reverse("office-index", args=[afghanistan.slug])
    res = django_app.get(url, user=afg_user)
    res = res.click(href="/profile/")
    res.forms["user-profile"]["language"] = "es"
    res.forms["user-profile"].submit().follow()
    afg_user.refresh_from_db()
    assert afg_user.language == "es"


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
