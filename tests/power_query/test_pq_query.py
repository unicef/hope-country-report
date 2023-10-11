from typing import TYPE_CHECKING

import pytest

from hope_country_report.apps.tenant.config import conf
from hope_country_report.state import state

if TYPE_CHECKING:
    from hope_country_report.apps.core.models import CountryOffice
    from hope_country_report.apps.hope.models import Household
    from hope_country_report.apps.power_query.models import Formatter, Query

pytestmark = pytest.mark.django_db()


@pytest.fixture()
def data(reporters):
    from testutils.factories import CountryOfficeFactory, HouseholdFactory, UserFactory, UserRoleFactory

    with state.set(must_tenant=False):
        co1: "CountryOffice" = CountryOfficeFactory(name="Afghanistan")
        co2: "CountryOffice" = CountryOfficeFactory(name="Niger")

        h1: "Household" = HouseholdFactory(business_area=co1.business_area)
        h2: "Household" = HouseholdFactory(business_area=co2.business_area)

        user = UserFactory(username="user", is_staff=False, is_superuser=False, is_active=True)
        UserRoleFactory(country_office=co1, group=reporters, user=user)

    # safety check
    assert h1.business_area != h2.business_area
    return {"co1": co1, "co2": co2, "h1": h1, "h2": h2, "user": user}


@pytest.fixture()
def query1(data):
    from testutils.factories import ContentTypeFactory, QueryFactory

    return QueryFactory(
        target=ContentTypeFactory(app_label="hope", model="household"),
        name="Query1",
        code="result=conn.all()",
    )


@pytest.fixture()
def query2(query1):
    from testutils.factories import QueryFactory

    return QueryFactory(name="Query2", code=f"result=invoke({query1.pk}, arguments)")


@pytest.fixture()
def formatter() -> "Formatter":
    from testutils.factories import FormatterFactory

    return FormatterFactory(name="Queryset To HTML")


@pytest.fixture()
def report(query1, formatter):
    from testutils.factories import ReportFactory

    return ReportFactory(formatter=formatter, query=query1)


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


def test_query_execution(query1: "Query"):
    from hope_country_report.apps.hope.models import Household

    assert Household.objects.count() == 2
    result = query1.run(persist=True)
    assert query1.datasets.exists()
    assert result[0].pk


# def test_query_lazy_execution(self) -> None:
#     self.query1.execute_matrix()
#     ds1 = self.query1.datasets.first()
#     ds2, __ = self.query1.run(use_existing=True)
#     self.assertEqual(ds1.pk, ds2.pk)
#
# def test_report_execution(self) -> None:
#     self.query1.execute_matrix()
#     dataset = self.query1.datasets.first()
#     self.report.execute()
#     self.assertTrue(self.report.documents.filter(dataset=dataset).exists())
#
# def test_nested_query(self) -> None:
#     result = self.query2.execute_matrix()
#     self.assertTrue(self.query2.datasets.exists())
#     self.assertEqual(result["{}"], self.query2.datasets.first().pk)
