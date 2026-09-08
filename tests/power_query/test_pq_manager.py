from typing import TYPE_CHECKING
from unittest import mock

import pytest
from django.db.models import Q

from hope_country_report.apps.power_query.manager import PowerQueryManager
from hope_country_report.state import state

if TYPE_CHECKING:
    from hope_country_report.apps.core.models import CountryOffice
    from hope_country_report.apps.power_query.models import Query


@pytest.fixture()
def manager():
    return PowerQueryManager()


@pytest.fixture()
def query(afghanistan: "CountryOffice"):
    from testutils.factories import QueryFactory

    return QueryFactory(country_office=afghanistan)


def test_get_tenant_filter_no_active_tenant(manager):
    from hope_country_report.apps.power_query.models import Query

    manager.model = Query
    assert manager.get_tenant_filter() == Q()


def test_get_tenant_filter_fail_closed_when_tenant_required_but_not_selected(manager):
    """Tenant isolation must never silently return all objects."""
    from unittest.mock import Mock

    from django.contrib.auth.models import User

    from hope_country_report.apps.power_query.models import Query

    manager.model = Query
    staff_user = User(username="staff", is_staff=True, is_superuser=False, is_active=True)
    request = Mock()
    request.user = staff_user
    with state.set(request=request, must_tenant=None, tenant=None, tenant_cookie=None):
        assert manager.get_tenant_filter() == Q(pk__in=[])


def test_get_tenant_filter_valid_tenant(manager, afghanistan):
    from hope_country_report.apps.power_query.models import Query

    manager.model = Query
    with state.set(must_tenant=True, tenant=afghanistan):
        assert manager.get_tenant_filter() == Q(country_office=afghanistan)


def test_get_tenant_filter_invalid_model(manager, afghanistan):
    from hope_country_report.apps.power_query.models import Query

    manager.model = Query
    with mock.patch("hope_country_report.apps.power_query.models.Query.Tenant.tenant_filter_field", ""):
        with pytest.raises(ValueError):
            with state.set(must_tenant=True, tenant=afghanistan):
                manager.get_tenant_filter()


def test_get_tenant_filter_all(manager, afghanistan):
    from hope_country_report.apps.power_query.models import Query

    manager.model = Query
    with mock.patch("hope_country_report.apps.power_query.models.Query.Tenant.tenant_filter_field", "__all__"):
        with state.set(must_tenant=True, tenant=afghanistan):
            assert manager.get_tenant_filter() == Q()


def test_get_queryset_active(manager, query: "Query"):
    from hope_country_report.apps.power_query.models import Query

    manager.model = Query
    with state.set(must_tenant=True, tenant=query.country_office):
        assert manager.get_queryset()


#
# def test_get_queryset_not_active(manager, household, afghanistan):
#     from hope_country_report.apps.hope.models import Household
#     manager.model = Household
#     with state.set(must_tenant=True, tenant=afghanistan):
#         assert not manager.get_queryset()
