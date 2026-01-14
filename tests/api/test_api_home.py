from typing import TYPE_CHECKING
from unittest import mock
from unittest.mock import Mock

import pytest
from rest_framework.test import APIClient
from testutils.factories import QueryFactory, ReportConfigurationFactory

from hope_country_report.state import state

if TYPE_CHECKING:
    from hope_country_report.apps.power_query.models import Query

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


@pytest.fixture()
def client(admin_user):
    c = APIClient()
    c.force_authenticate(user=admin_user)
    return c


def test_api_root(client):
    url = "/api/"
    res = client.get(url)
    assert res.json()


def test_api_home(client):
    url = "/api/home/"
    res = client.get(url)
    assert res.status_code == 200
    assert res.json() == {}


def test_api_topology(client, data):
    url = "/api/home/topology/"
    res = client.get(url)
    assert res.status_code == 200
    assert res.json()


def test_api_boundaries(client, data):
    url = "/api/home/boundaries/"
    res = client.get(url)
    assert res.status_code == 200
    assert res.json()


def test_api_offices(client, data):
    url = "/api/home/offices/"
    res = client.get(url)
    assert res.status_code == 200
