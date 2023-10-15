from typing import TYPE_CHECKING

import pytest

from hope_country_report.state import state

if TYPE_CHECKING:
    from hope_country_report.apps.core.models import CountryOffice


@pytest.fixture()
def data(reporters):
    from testutils.factories import CountryFactory, CountryOfficeFactory, HouseholdFactory, UserFactory, UserRoleFactory

    with state.set(must_tenant=False):
        co1: "CountryOffice" = CountryOfficeFactory(name="Afghanistan")
        co2: "CountryOffice" = CountryOfficeFactory(name="Niger")
        co3: "CountryOffice" = CountryOfficeFactory(name="Sudan")

        CountryFactory()
        CountryFactory()
        CountryFactory()

        HouseholdFactory(business_area=co1.business_area, withdrawn=True)
        HouseholdFactory(business_area=co1.business_area, withdrawn=False)
        HouseholdFactory(business_area=co2.business_area, withdrawn=True)
        HouseholdFactory(business_area=co2.business_area, withdrawn=False)

        user = UserFactory(username="user", is_staff=False, is_superuser=False, is_active=True)
        UserRoleFactory(country_office=co1, group=reporters, user=user)

    return {"Afghanistan": co1, "Niger": co2, "Sudan": co3}


@pytest.mark.parametrize("co,expected", [("Afghanistan", 2), ("Niger", 2), ("Sudan", 0)])
def test_filtering(data, co, expected):
    from hope_country_report.apps.hope.models import Household

    assert Household.objects.count() == 4
    with state.set(tenant=data[co], must_tenant=True):
        assert Household.objects.count() == expected


@pytest.mark.parametrize("co", ["Afghanistan", "Niger", "Sudan"])
def test_no_filtering(data, co):
    from hope_country_report.apps.hope.models import Country

    assert Country.objects.count() == 3
    with state.set(tenant=data[co], must_tenant=True):
        assert Country.objects.count() == 3
