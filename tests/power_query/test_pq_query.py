from typing import TYPE_CHECKING

import pytest

from hope_country_report.apps.tenant.config import conf
from hope_country_report.state import state

if TYPE_CHECKING:
    from hope_country_report.apps.core.models import CountryOffice
    from hope_country_report.apps.hope.models import Household
    from hope_country_report.apps.power_query.models import Query

pytestmark = pytest.mark.django_db()


@pytest.fixture()
def data(tenant_user):
    from testutils.factories import CountryOfficeFactory, HouseholdFactory

    with state.set(must_tenant=False):
        # co1: "CountryOffice" = CountryOfficeFactory(name="Afghanistan", code=1)
        co1: "CountryOffice" = tenant_user.roles.first().country_office
        co2: "CountryOffice" = CountryOfficeFactory(name="Ukraine", code=2)
        # co2: "CountryOffice" = CountryOfficeFactory()
        h1: "Household" = HouseholdFactory(business_area=co1.business_area)
        h2: "Household" = HouseholdFactory(business_area=co2.business_area)

    return {"co1": co1, "co2": co2, "h1": h1, "h2": h2, "user": tenant_user}


@pytest.fixture()
def req(rf, data):
    req = rf.get("/")
    req.user = data["user"]
    req.COOKIES[conf.COOKIE_NAME] = data["user"].roles.first().country_office.slug
    yield req


def test_filter_query(req, data):
    from testutils.factories import QueryFactory

    tenant_slug = data["h1"].business_area.id
    tenant = data["h1"].business_area.country_office

    with state.configure(request=req, tenant=tenant, must_tenant=True, tenant_cookie=tenant_slug):
        q: "Query" = QueryFactory(owner=data["user"], project=state.tenant)
        qs, extra = q.run()
        assert qs.count() == 1
        assert qs.first() == data["h1"]
