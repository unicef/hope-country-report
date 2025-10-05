from typing import TYPE_CHECKING

from uuid import UUID

import pytest

from django.conf import settings

from freezegun import freeze_time

from hope_country_report.apps.tenant.config import conf
from hope_country_report.state import state

if TYPE_CHECKING:
    from typing import TypedDict

    from hope_country_report.apps.core.models import CountryOffice, User
    from hope_country_report.apps.hope.models import Household
    from hope_country_report.apps.power_query.models import Dataset, Formatter, Parametrizer, Query

    class _DATA(TypedDict):
        user: User
        co1: CountryOffice
        co2: CountryOffice
        hh1: tuple[Household, Household]
        hh2: tuple[Household, Household]


pytestmark = pytest.mark.django_db()


@pytest.fixture()
def data(reporters) -> "_DATA":
    from testutils.factories import CountryOfficeFactory, HouseholdFactory, UserFactory, UserRoleFactory

    with state.set(must_tenant=False):
        co1: "CountryOffice" = CountryOfficeFactory(name="Afghanistan")
        co2: "CountryOffice" = CountryOfficeFactory(name="Niger")

        h11: "Household" = HouseholdFactory(unicef_id="u1", business_area=co1.business_area, withdrawn=True)
        h12: "Household" = HouseholdFactory(unicef_id="u2", business_area=co1.business_area, withdrawn=False)
        h21: "Household" = HouseholdFactory(unicef_id="u3", business_area=co2.business_area, withdrawn=True)
        h22: "Household" = HouseholdFactory(unicef_id="u4", business_area=co2.business_area, withdrawn=False)

        user = UserFactory(username="user", is_staff=False, is_superuser=False, is_active=True)
        UserRoleFactory(country_office=co1, group=reporters, user=user)

    # safety check
    return {"co1": co1, "co2": co2, "hh1": (h11, h12), "hh2": (h21, h22), "user": user}


@pytest.fixture()
def query(data: "_DATA"):
    from testutils.factories import ContentTypeFactory, QueryFactory

    return QueryFactory(
        target=ContentTypeFactory(app_label="hope", model="household"),
        name="Query",
        code="result=conn.all()",
    )


@pytest.fixture()
def query_nested(query):
    from testutils.factories import QueryFactory

    return QueryFactory(name="Nested Query", code=f"result=invoke({query.pk}, arguments)")


@pytest.fixture()
def query_parametrizer(data: "_DATA"):
    from testutils.factories import ParametrizerFactory, QueryFactory

    parametrizer: "Parametrizer" = ParametrizerFactory(value={"withdrawn": [True, False]})
    return QueryFactory(
        name="Query Parametrizer",
        code="result=conn.filter(withdrawn=arguments['withdrawn'])",
        parametrizer=parametrizer,
    )


@pytest.fixture()
def query_impl(data: "_DATA", query):
    from testutils.factories import QueryFactory

    return QueryFactory(
        target=None,
        name="Query Implement",
        parent=query,
        country_office=data["co1"],
        code=None,
    )


@pytest.fixture()
def query_log(data: "_DATA"):
    from testutils.factories import ParametrizerFactory, QueryFactory

    parametrizer: "Parametrizer" = ParametrizerFactory(value={"withdrawn": [True, False]})
    return QueryFactory(
        name="Query Parametrizer",
        code="""debug("start")
result=conn.all()
debug("end")
""",
        parametrizer=parametrizer,
    )


@pytest.fixture()
def formatter() -> "Formatter":
    from testutils.factories import FormatterFactory

    return FormatterFactory(name="Queryset To HTML")


#
# @pytest.fixture()
# def report(query, formatter):
#     from testutils.factories import ReportFactory
#
#     return ReportFactory(formatter=formatter, query=query)


@pytest.fixture()
def req(rf, data):
    req = rf.get("/")
    req.user = data["user"]
    req.COOKIES[conf.COOKIE_NAME] = data["user"].roles.first().country_office.slug
    yield req


def test_filter_query(req, data: "_DATA"):
    from testutils.factories import QueryFactory

    tenant_slug = data["hh1"][0].business_area.id
    tenant = data["hh1"][0].business_area.country_office
    assert tenant  # safety check
    with state.configure(request=req, tenant=tenant, must_tenant=True, tenant_cookie=tenant_slug):
        q: "Query" = QueryFactory(owner=data["user"], country_office=state.tenant)
        ds, extra = q.run()
        assert ds.data.count() == 2
        assert ds.data.first().pk == UUID(data["hh1"][0].pk)


def test_query_execution(query: "Query"):
    from hope_country_report.apps.hope.models import Household

    assert Household.objects.count() == 4
    result = query.run(persist=True)
    assert query.datasets.exists()
    assert result[0].data[0].pk


def test_nested_query(query_nested: "Query"):
    result = query_nested.execute_matrix()
    assert query_nested.datasets.exists()
    assert result["{}"] == query_nested.datasets.first().pk


def test_query_impl(query_impl: "Query", data):
    from hope_country_report.apps.hope.models import Household

    tenant_slug = data["hh1"][0].business_area.id
    tenant = data["hh1"][0].business_area.country_office

    with state.configure(request=req, tenant=tenant, must_tenant=True, tenant_cookie=tenant_slug):
        result = query_impl.run(persist=True)

    assert Household.objects.count() == 4
    assert query_impl.get_code() == query_impl.parent.code
    assert query_impl.datasets.exists()
    assert result[0].data[0].pk
    assert not query_impl.parent.datasets.exists()
    assert set(query_impl.datasets.first().data) == set(Household.objects.filter(business_area__id=tenant_slug))


def test_query_parametrizer(query_parametrizer: "Query"):
    result = query_parametrizer.execute_matrix()
    assert query_parametrizer.datasets.count() == 2
    assert sorted(result.keys()) == ["{'withdrawn': False}", "{'withdrawn': True}"]
    ds: "Dataset" = query_parametrizer.datasets.get(info__arguments__withdrawn=False)
    assert ds.data.filter(withdrawn=False).count() == ds.data.count() == 2

    ds: "Dataset" = query_parametrizer.datasets.get(info__arguments__withdrawn=True)
    assert ds.data.filter(withdrawn=True).count() == ds.data.count() == 2


def test_query_silk(query: "Query", data):
    query.datasets.all().delete()
    tenant_slug = data["hh1"][0].business_area.id
    tenant = data["hh1"][0].business_area.country_office
    uid = str(data["hh1"][0].business_area.pk)
    with state.configure(request=req, tenant=tenant, must_tenant=True, tenant_cookie=tenant_slug):
        ds, extra = query.run()
    assert ds.data.count() == 2
    assert ds.data.first().pk == UUID(data["hh1"][0].pk)
    db_info = ds.info["perfs"]["db"][settings.POWER_QUERY_DB_ALIAS]
    assert db_info["count"] == 1
    assert f'WHERE "_hope_ro__hope_household"."business_area_id" = \'{uid}\'::uuid' in db_info["queries"][0]


@freeze_time("2012-01-14 08:00:00")
def test_query_log(query_log: "Query", data):
    tenant_slug = data["hh1"][0].business_area.id
    tenant = data["hh1"][0].business_area.country_office
    with state.configure(request=req, tenant=tenant, must_tenant=True, tenant_cookie=tenant_slug):
        ds, extra = query_log.run()
    assert ds.data.count() == 2
    assert ds.data.first().pk == UUID(data["hh1"][0].pk)
    assert ds.info["debug"] == [("08:00:00", "start"), ("08:00:00", "end")]


@freeze_time("2012-01-14 08:00:00")
def test_query_marshalling(query: "Query", data):
    tenant_slug = data["hh1"][0].business_area.id
    tenant = data["hh1"][0].business_area.country_office
    with state.configure(request=req, tenant=tenant, must_tenant=True, tenant_cookie=tenant_slug):
        ds, extra = query.run()
    assert ds.data.count() == 2
    assert ds.data.first().pk == UUID(data["hh1"][0].pk)
