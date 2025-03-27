import pytest
from unittest import mock
from unittest.mock import Mock

from rest_framework.test import APIClient
from testutils.factories import ChartPageFactory, QueryFactory, ReportConfigurationFactory

from hope_country_report.apps.power_query.models import Query, ReportDocument
from hope_country_report.state import state

pytestmark = [pytest.mark.api, pytest.mark.django_db]

# WE DO NOT USE REVERSE HERE. WE NEED TO CHECK ENDPOINTS CONTRACTS


@pytest.fixture(autouse=True)
def data(afg_user):
    with state.set(must_tenant=False):
        query: Query = QueryFactory(country_office=afg_user._afghanistan, owner=afg_user)
        with mock.patch("hope_country_report.apps.power_query.models.report.notify_report_completion", Mock()):
            config = ReportConfigurationFactory(query=query, country_office=afg_user._afghanistan, owner=query.owner)

        config.execute()
        doc = config.documents.first()

    return {
        "co": query.country_office,
        "query": query,
        "report": config,
        "doc": doc,
    }


@pytest.fixture
def admin_user_with_permission(admin_user):
    """Admin user with the necessary permissions added for ChartPage."""
    from django.contrib.auth.models import Permission
    from django.contrib.contenttypes.models import ContentType

    from hope_country_report.apps.power_query.models import ChartPage

    content_type = ContentType.objects.get_for_model(ChartPage)
    view_permission = Permission.objects.get(codename="view_chartpage", content_type=content_type)
    admin_user.user_permissions.add(view_permission)
    assert admin_user.has_perm("power_query.view_chartpage"), "User does not have view_chartpage permission"
    return admin_user


@pytest.fixture
def client(admin_user_with_permission):
    c = APIClient()
    c.force_authenticate(user=admin_user_with_permission)
    assert admin_user_with_permission.is_authenticated, "User is not authenticated properly"
    return c


@pytest.mark.django_db
def test_api_chart_list(client, data, admin_user_with_permission):
    url = f"/{data['co'].slug}/charts/"
    client.force_login(admin_user_with_permission)
    res = client.get(url)
    assert res.status_code == 200
    content = res.content.decode()
    assert "ChartListView" in content, "Expected 'Charts' to be in the response HTML"


@pytest.mark.django_db
def test_api_chart_detail(client, data, admin_user_with_permission):
    chart_page = ChartPageFactory(country_office=data["co"], query=data["query"])
    url = f"/{data['co'].slug}/charts/{chart_page.pk}/"
    client.force_login(admin_user_with_permission)
    res = client.get(url)
    assert res.status_code == 200
    content = res.content.decode()
    assert chart_page.title in content, f"Expected chart title '{chart_page.title}' to be in the response HTML"


def test_api_office_list(client, data):
    url = "/api/offices/"
    res = client.get(url)
    assert res.json()


def test_api_query_list(client, data):
    url = f"/api/offices/{data['co'].slug}/queries/"
    res = client.get(url)
    assert res.json()


def test_api_query(client, data):
    url = f"/api/offices/{data['co'].slug}/queries/{data['query'].pk}/"
    res = client.get(url)
    assert res.json()["id"] == data["query"].pk


def test_api_report_list(client, data):
    url = f"/api/offices/{data['co'].slug}/config/"
    res = client.get(url)
    assert res.json()


def test_api_report(client, data):
    url = f"/api/offices/{data['co'].slug}/config/{data['report'].pk}/"
    res = client.get(url)
    assert res.json()["id"] == data["report"].pk


def test_api_document_list(client, data):
    url = f"/api/offices/{data['co'].slug}/config/{data['report'].pk}/documents/"
    res = client.get(url)
    assert res.json()


def test_api_document(client, data):
    url = f"/api/offices/{data['co'].slug}/config/{data['report'].pk}/documents/{data['doc'].pk}/"
    res = client.get(url)
    assert res.json()["id"] == data["doc"].pk


def test_api_document_download(client, data):
    url = f"/api/offices/{data['co'].slug}/config/{data['report'].pk}/documents/{data['doc'].pk}/download/"
    res = client.get(url)
    assert res.headers["Content-Type"] == "application/force-download"


def test_api_document_download_no_file(client, data):
    url = f"/api/offices/{data['co'].slug}/config/{data['report'].pk}/documents/{data['doc'].pk}/download/"
    doc = Mock(spec=ReportDocument)()
    doc.file.size = 0
    with mock.patch("hope_country_report.api.views.ReportDocument.objects.get", lambda **k: doc):
        res = client.get(url)
    assert res.status_code == 404
