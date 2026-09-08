import pytest
from rest_framework.test import APIClient

from hope_country_report.apps.core.models import CountryOffice
from hope_country_report.state import state

pytestmark = [pytest.mark.api, pytest.mark.django_db]


@pytest.fixture()
def data(afg_user, afghanistan):
    from testutils.factories import (
        ChartPageFactory,
        CountryOfficeFactory,
        QueryFactory,
        ReportConfigurationFactory,
        UserFactory,
    )
    from unittest import mock
    from unittest.mock import Mock

    niger = CountryOfficeFactory(name="Niger")
    sudan = CountryOfficeFactory(name="Sudan")
    with state.set(must_tenant=False):
        query_afg = QueryFactory(country_office=afghanistan, owner=afg_user)
        query_niger = QueryFactory(country_office=niger, owner=afg_user)
        ChartPageFactory(country_office=afghanistan, query=query_afg, title="AFG chart")
        ChartPageFactory(country_office=niger, query=query_niger, title="NER chart")
        ChartPageFactory(
            country_office=sudan,
            query=QueryFactory(country_office=sudan, owner=UserFactory()),
            title="SSD chart",
        )
        with mock.patch("hope_country_report.apps.power_query.models.report.notify_report_completion", Mock()):
            ReportConfigurationFactory(query=query_niger, country_office=niger, owner=afg_user)
    return {
        "co": afghanistan,
        "niger": niger,
        "sudan": sudan,
        "query_afg": query_afg,
        "query_niger": query_niger,
    }


def _grant(user, model, codename):
    from django.contrib.auth.models import Permission
    from django.contrib.contenttypes.models import ContentType

    ct = ContentType.objects.get_for_model(model)
    perm = Permission.objects.get(content_type=ct, codename=codename)
    user.user_permissions.add(perm)


def _results(payload):
    if isinstance(payload, dict) and "results" in payload:
        return payload["results"]
    return payload


def test_api_offices_list_scoped_to_user_roles(afg_user, data):
    """Setting the office must not list offices the user has no role in."""
    _grant(afg_user, CountryOffice, "view_countryoffice")
    client = APIClient()
    client.force_authenticate(user=afg_user)
    res = client.get("/api/offices/")
    assert res.status_code == 200
    slugs = [o["slug"] for o in res.json()]
    assert data["co"].slug in slugs
    assert data["niger"].slug not in slugs
    assert data["sudan"].slug not in slugs


def test_api_top_level_queries_scoped_to_user_roles(afg_user, data):
    client = APIClient()
    client.force_authenticate(user=afg_user)
    res = client.get("/api/queries/")
    assert res.status_code == 200
    ids = [q["id"] for q in _results(res.json())]
    assert data["query_afg"].pk in ids
    assert data["query_niger"].pk not in ids


def test_api_cross_tenant_query_retrieve_404(afg_user, data):
    client = APIClient()
    client.force_authenticate(user=afg_user)
    url = f"/api/offices/{data['niger'].slug}/queries/{data['query_niger'].pk}/"
    res = client.get(url)
    assert res.status_code == 404


def test_api_top_level_charts_scoped_to_user_roles(afg_user, data):
    client = APIClient()
    client.force_authenticate(user=afg_user)
    res = client.get("/api/charts/")
    assert res.status_code == 200
    titles = [c["title"] for c in _results(res.json())]
    assert "AFG chart" in titles
    assert "NER chart" not in titles
    assert "SSD chart" not in titles


def test_api_document_download_restricted_denied(afg_user, afghanistan):
    """A document restricted to specific users must not be downloadable by others."""
    from testutils.factories import ReportDocumentFactory, UserFactory


    owner = UserFactory(username="owner")
    allowed = UserFactory(username="allowed")
    doc = ReportDocumentFactory(
        report__name="Restricted report", report__owner=owner, report__country_office=afghanistan
    )
    doc.report.limit_access_to.add(allowed)

    url = f"/api/offices/{afghanistan.slug}/config/{doc.report.pk}/documents/{doc.pk}/download/"
    client = APIClient()
    client.force_authenticate(user=afg_user)
    res = client.get(url)
    assert res.status_code == 403


def test_api_document_restricted_retrieve_denied(afg_user, afghanistan):
    from testutils.factories import ReportDocumentFactory, UserFactory


    owner = UserFactory(username="owner2")
    allowed = UserFactory(username="allowed2")
    doc = ReportDocumentFactory(
        report__name="Restricted report 2", report__owner=owner, report__country_office=afghanistan
    )
    doc.report.limit_access_to.add(allowed)

    url = f"/api/offices/{afghanistan.slug}/config/{doc.report.pk}/documents/{doc.pk}/"
    client = APIClient()
    client.force_authenticate(user=afg_user)
    res = client.get(url)
    # Denied: redirected to the request-access page (same behaviour as the web view).
    assert res.status_code == 302
    assert res.headers["Location"] == f"/{afghanistan.slug}/request-access/{doc.report.pk}/"
