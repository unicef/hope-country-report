from typing import TYPE_CHECKING

import pytest
from unittest import mock

from hope_country_report.apps.tenant.db import TenantManager
from hope_country_report.apps.tenant.exceptions import InvalidTenantError
from hope_country_report.state import state

if TYPE_CHECKING:
    from hope_country_report.apps.core.models import CountryOffice


@pytest.fixture()
def manager():
    return TenantManager()


@pytest.fixture()
def household(afghanistan: "CountryOffice"):
    from testutils.factories import HouseholdFactory

    return HouseholdFactory(business_area=afghanistan.business_area)


def test_get_tenant_filter_no_active_tenant(manager):
    from hope_country_report.apps.hope.models import Household

    manager.model = Household
    assert manager.get_tenant_filter() == {}


def test_get_tenant_filter_invalid_tenant(manager, afghanistan):
    from hope_country_report.apps.hope.models import Household

    manager.model = Household
    with pytest.raises(InvalidTenantError):
        with state.set(must_tenant=True):
            manager.get_tenant_filter()


def test_get_tenant_filter_valid_tenant(manager, afghanistan):
    from hope_country_report.apps.hope.models import Household

    manager.model = Household
    with state.set(must_tenant=True, tenant=afghanistan):
        assert manager.get_tenant_filter() == {"business_area": afghanistan.hope_id}


def test_get_tenant_filter_invalid_model(manager, afghanistan):
    from hope_country_report.apps.hope.models import Household

    manager.model = Household
    with mock.patch("hope_country_report.apps.hope.models.Household.Tenant.tenant_filter_field", ""):
        with pytest.raises(ValueError):
            with state.set(must_tenant=True, tenant=afghanistan):
                manager.get_tenant_filter()


def test_get_tenant_filter_all(manager, afghanistan):
    from hope_country_report.apps.hope.models import Household

    manager.model = Household
    with mock.patch("hope_country_report.apps.hope.models.Household.Tenant.tenant_filter_field", "__all__"):
        with state.set(must_tenant=True, tenant=afghanistan.business_area):
            assert manager.get_tenant_filter() == {}


#
#
# def test_get_queryset_active(manager, household: "Household"):
#     from hope_country_report.apps.hope.models import Household
#
#     manager.model = Household
#     with state.set(must_tenant=True, tenant=household.business_area):
#         assert manager.get_queryset()
#

#
# def test_get_queryset_not_active(manager, household, country_office):
#     from hope_country_report.apps.hope.models import Household
#     manager.model = Household
#     with state.set(must_tenant=True, tenant=country_office):
#         assert not manager.get_queryset()
