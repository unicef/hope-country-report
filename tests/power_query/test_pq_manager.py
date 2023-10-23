from typing import TYPE_CHECKING

import pytest
from unittest import mock

from django.db.models import Q

from hope_country_report.apps.power_query.models import PowerQueryManager
from hope_country_report.apps.tenant.exceptions import InvalidTenantError
from hope_country_report.state import state

if TYPE_CHECKING:
    from hope_country_report.apps.core.models import CountryOffice
    from hope_country_report.apps.power_query.models import Query


@pytest.fixture()
def manager():
    return PowerQueryManager()


@pytest.fixture()
def query(country_office: "CountryOffice"):
    from testutils.factories import QueryFactory

    return QueryFactory(country_office=country_office)


def test_get_tenant_filter_no_active_tenant(manager):
    from hope_country_report.apps.power_query.models import Query

    manager.model = Query
    assert manager.get_tenant_filter() == Q()


def test_get_tenant_filter_invalid_tenant(manager, country_office):
    from hope_country_report.apps.power_query.models import Query

    manager.model = Query
    with pytest.raises(InvalidTenantError):
        with state.set(must_tenant=True):
            manager.get_tenant_filter()


def test_get_tenant_filter_valid_tenant(manager, country_office):
    from hope_country_report.apps.power_query.models import Query

    manager.model = Query
    with state.set(must_tenant=True, tenant=country_office):
        assert manager.get_tenant_filter() == Q(country_office=country_office)


def test_get_tenant_filter_invalid_model(manager, country_office):
    from hope_country_report.apps.power_query.models import Query

    manager.model = Query
    with mock.patch("hope_country_report.apps.power_query.models.Query.Tenant.tenant_filter_field", ""):
        with pytest.raises(ValueError):
            with state.set(must_tenant=True, tenant=country_office):
                manager.get_tenant_filter()


def test_get_tenant_filter_all(manager, country_office):
    from hope_country_report.apps.power_query.models import Query

    manager.model = Query
    with mock.patch("hope_country_report.apps.power_query.models.Query.Tenant.tenant_filter_field", "__all__"):
        with state.set(must_tenant=True, tenant=country_office):
            assert manager.get_tenant_filter() == Q()


def test_get_queryset_active(manager, query: "Query"):
    from hope_country_report.apps.power_query.models import Query

    manager.model = Query
    with state.set(must_tenant=True, tenant=query.country_office):
        assert manager.get_queryset()


#
# def test_get_queryset_not_active(manager, household, country_office):
#     from hope_country_report.apps.hope.models import Household
#     manager.model = Household
#     with state.set(must_tenant=True, tenant=country_office):
#         assert not manager.get_queryset()
