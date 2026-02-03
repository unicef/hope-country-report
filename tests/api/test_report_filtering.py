import pytest
from rest_framework.test import APIClient
from testutils.factories import ReportConfigurationFactory, QueryFactory
from hope_country_report.state import state

pytestmark = [pytest.mark.api, pytest.mark.django_db]


@pytest.fixture(autouse=True)
def data(afg_user):
    with state.set(must_tenant=False):
        query = QueryFactory(country_office=afg_user._afghanistan, owner=afg_user)
        report1 = ReportConfigurationFactory(
            query=query, country_office=afg_user._afghanistan, owner=query.owner, title="Report One", name="report-one"
        )
        report2 = ReportConfigurationFactory(
            query=query, country_office=afg_user._afghanistan, owner=query.owner, title="Report Two", name="report-two"
        )
    return {
        "co": query.country_office,
        "report1": report1,
        "report2": report2,
    }


@pytest.fixture()
def client(admin_user):
    c = APIClient()
    c.force_authenticate(user=admin_user)
    return c


def test_api_report_filter_by_name(client, data):
    url = f"/api/offices/{data['co'].slug}/config/?name=report-one"
    res = client.get(url)
    assert res.status_code == 200
    json_data = res.json()

    assert len(json_data) == 1
    assert json_data[0]["name"] == "report-one"

    url = f"/api/offices/{data['co'].slug}/config/?name=report-two"
    res = client.get(url)
    assert res.status_code == 200
    json_data = res.json()
    assert len(json_data) == 1
    assert json_data[0]["name"] == "report-two"
