import pytest

from rest_framework.test import APIClient

from hope_country_report.apps.power_query.models import Query
from testutils.factories import QueryFactory

pytestmark = [pytest.mark.api, pytest.mark.django_db]

# WE DO NOT USE REVERSE HERE. WE NEED TO CHECK ENDPOINTS CONTRACTS


@pytest.fixture(autouse=True)
def data(afg_user):
    query: "Query" = QueryFactory(
        owner=afg_user,
        name="Debug Query",
        curr_async_result_id=None,
        code="""result=[1,2,3,4]""",
    )
    return {"query": query, "co": query.country_office}


@pytest.fixture()
def client(admin_user):
    c = APIClient()
    c.force_authenticate(user=admin_user)
    return c


def test_api_root(client):
    url = "/api/"
    res = client.get(url)
    assert res.json()


def test_api_offices(client, data):
    url = "/api/offices/"
    res = client.get(url)
    assert res.json()


def test_api_queries(client, data):
    url = f"/api/offices/{data['co'].slug}/queries/"
    res = client.get(url)
    assert res.json()[0]["id"] == data["query"].pk


def test_api_query(client, data):
    url = f"/api/offices/{data['co'].slug}/queries/{data['query'].pk}/"
    res = client.get(url)
    assert res.json()["id"] == data["query"].pk
