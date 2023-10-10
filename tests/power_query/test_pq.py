from typing import TYPE_CHECKING

import pytest

from hope_country_report.state import state

if TYPE_CHECKING:
    from hope_country_report.apps.core.models import CountryOffice
    from hope_country_report.apps.hope.models import Household
    from hope_country_report.apps.power_query.models import Query


pytestmark = pytest.mark.django_db(databases=["default", "hope_ro"])


@pytest.fixture()
def data():
    from testutils.factories import CountryOfficeFactory, HouseholdFactory

    co1: "CountryOffice" = CountryOfficeFactory()
    co2: "CountryOffice" = CountryOfficeFactory()
    assert co1 != co2
    h1: "Household" = HouseholdFactory(business_area=co1.business_area)
    h2: "Household" = HouseholdFactory(business_area=co2.business_area)
    assert h1.pk != h2.pk
    assert h1.head_of_household
    assert h2.head_of_household
    return {"co1": co1, "co2": co2, "h1": h1, "h2": h2}


def test_filter_query(tenant_user, data):
    from testutils.factories import QueryFactory

    q: "Query" = QueryFactory()
    # with state.set(tenant=data["co1"].slug, tenant_instance=None, persist=False):
    result = q.run()
    assert state.filters == []
    assert result == ""
