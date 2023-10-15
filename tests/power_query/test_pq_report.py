# from typing import TYPE_CHECKING
#
# import contextlib
#
# import pytest
#
# from django.conf import settings
#
# import sqlparse
# from flags import state as flag_state
# from freezegun import freeze_time
#
# from hope_country_report.apps.tenant.config import conf
# from hope_country_report.state import state
#
# if TYPE_CHECKING:
#     from typing import Tuple, TypedDict
#
#     from hope_country_report.apps.core.models import CountryOffice, User
#     from hope_country_report.apps.hope.models import Household
#     from hope_country_report.apps.power_query.models import Dataset, Formatter, Parametrizer, Query
#
#     _DATA = TypedDict(
#         "_DATA",
#         {
#             "user": User,
#             "co1": CountryOffice,
#             "co2": CountryOffice,
#             "hh1": Tuple[Household, Household],
#             "hh2": Tuple[Household, Household],
#         },
#     )
#
# pytestmark = pytest.mark.django_db()
#
#
# @contextlib.contextmanager
# def enable_flag(name):
#     flag_state.enable_flag(name)
#     yield
#     flag_state.disable_flag(name)
#
#
# @pytest.fixture()
# def data(reporters) -> "_DATA":
#     from testutils.factories import CountryOfficeFactory, HouseholdFactory, UserFactory, UserRoleFactory
#
#     with state.set(must_tenant=False):
#         co1: "CountryOffice" = CountryOfficeFactory(name="Afghanistan")
#         co2: "CountryOffice" = CountryOfficeFactory(name="Niger")
#
#         h11: "Household" = HouseholdFactory(business_area=co1.business_area, withdrawn=True)
#         h12: "Household" = HouseholdFactory(business_area=co1.business_area, withdrawn=False)
#         h21: "Household" = HouseholdFactory(business_area=co2.business_area, withdrawn=True)
#         h22: "Household" = HouseholdFactory(business_area=co2.business_area, withdrawn=False)
#
#         user = UserFactory(username="user", is_staff=False, is_superuser=False, is_active=True)
#         UserRoleFactory(country_office=co1, group=reporters, user=user)
#
#     # safety check
#     return {"co1": co1, "co2": co2, "hh1": (h11, h12), "hh2": (h21, h22), "user": user}
#
#
# @pytest.fixture()
# def query1(data: "_DATA"):
#     from testutils.factories import ContentTypeFactory, QueryFactory
#
#     return QueryFactory(
#         target=ContentTypeFactory(app_label="hope", model="household"),
#         name="Query1",
#         code="result=conn.all()",
#     )
#
#
# @pytest.fixture()
# def query2(query1):
#     from testutils.factories import QueryFactory
#
#     return QueryFactory(name="Query2", code=f"result=invoke({query1.pk}, arguments)")
#
#
# @pytest.fixture()
# def query3(data: "_DATA"):
#     from testutils.factories import ParametrizerFactory, QueryFactory
#
#     parametrizer: "Parametrizer" = ParametrizerFactory(value={"withdrawn": [True, False]})
#     return QueryFactory(
#         name="Query3", code="result=conn.filter(withdrawn=arguments['withdrawn'])", parametrizer=parametrizer
#     )
#
#
# @pytest.fixture()
# def query_log(data: "_DATA"):
#     from testutils.factories import ParametrizerFactory, QueryFactory
#
#     parametrizer: "Parametrizer" = ParametrizerFactory(value={"withdrawn": [True, False]})
#     return QueryFactory(
#         name="Query3",
#         code="""debug("start")
# result=conn.all()
# debug("end")
# """,
#         parametrizer=parametrizer,
#     )
#
#
# @pytest.fixture()
# def formatter() -> "Formatter":
#     from testutils.factories import FormatterFactory
#
#     return FormatterFactory(name="Queryset To HTML")
#
# #
# # @pytest.fixture()
# # def report(query1, formatter):
# #     from testutils.factories import ReportFactory
# #
# #     return ReportFactory(formatter=formatter, query=query1)
#
#
# @pytest.fixture()
# def req(rf, data):
#     req = rf.get("/")
#     req.user = data["user"]
#     req.COOKIES[conf.COOKIE_NAME] = data["user"].roles.first().country_office.slug
#     yield req
#
#
# def test_filter_query(req, data: "_DATA"):
#     from testutils.factories import QueryFactory
#
#     tenant_slug = data["hh1"][0].business_area.id
#     tenant = data["hh1"][0].business_area.country_office
#
#     with state.configure(request=req, tenant=tenant, must_tenant=True, tenant_cookie=tenant_slug):
#         q: "Query" = QueryFactory(owner=data["user"], project=state.tenant)
#         qs, extra = q.run()
#         assert qs.count() == 2
#         assert qs.first() == data["hh1"][0]
#
#
# def test_query_execution(query1: "Query"):
#     from hope_country_report.apps.hope.models import Household
#
#     assert Household.objects.count() == 4
#     result = query1.run(persist=True)
#     assert query1.datasets.exists()
#     assert result[0].pk
#
#
# def test_nested_query(query2: "Query"):
#     result = query2.execute_matrix()
#     assert query2.datasets.exists()
#     assert result["{}"] == query2.datasets.first().pk
#
#
# def test_query_parametrizer(query3: "Query"):
#     result = query3.execute_matrix()
#     assert query3.datasets.count() == 2
#     assert sorted(result.keys()) == ["timestamp", "{'withdrawn': False}", "{'withdrawn': True}"]
#     ds: "Dataset" = query3.datasets.get(info__arguments__withdrawn=False)
#     assert ds.data.filter(withdrawn=False).count() == ds.data.count() == 2
#
#     ds: "Dataset" = query3.datasets.get(info__arguments__withdrawn=True)
#     assert ds.data.filter(withdrawn=True).count() == ds.data.count() == 2
#
#
# def test_query_silk(query1: "Query", data):
#     tenant_slug = data["hh1"][0].business_area.id
#     tenant = data["hh1"][0].business_area.country_office
#     with state.configure(request=req, tenant=tenant, must_tenant=True, tenant_cookie=tenant_slug):
#         qs, info = query1.run()
#     assert qs.count() == 2
#     assert qs.first() == data["hh1"][0]
#     db_info = info["perfs"]["db"][settings.POWER_QUERY_DB_ALIAS]
#     assert db_info["count"] == 1
#     assert db_info["queries"][0][1] == (tenant_slug,)
#     parsed = sqlparse.parse(db_info["queries"][0][0])[0]
#     assert parsed[-1].value == 'WHERE "_hope_ro__hope_household"."business_area_id" = %s'
#
#
# @freeze_time("2012-01-14 08:00:00")
# def test_query_log(query_log: "Query", data):
#     tenant_slug = data["hh1"][0].business_area.id
#     tenant = data["hh1"][0].business_area.country_office
#     with state.configure(request=req, tenant=tenant, must_tenant=True, tenant_cookie=tenant_slug):
#         qs, info = query_log.run()
#     assert qs.count() == 2
#     assert qs.first() == data["hh1"][0]
#     assert info["debug"] == [("08:00:00", "start"), ("08:00:00", "end")]
