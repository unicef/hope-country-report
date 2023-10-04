import contextlib
from typing import TYPE_CHECKING

import pytest

from hope_country_report.state import state

if TYPE_CHECKING:
    from django.contrib.auth.models import Group

    from hope_country_report.apps.core.models import CountryOffice, UserRole
    from hope_country_report.types.http import AuthHttpRequest


@pytest.fixture()
def anonymous():
    from django.contrib.auth.models import AnonymousUser

    return AnonymousUser()


@pytest.fixture()
def req(request, rf) -> "AuthHttpRequest":
    req: "AuthHttpRequest" = rf.get("/")
    current = state.request
    state.request = req
    yield req
    state.request = current


@pytest.fixture()
def country_office(db):
    from testutils.factories import CountryOfficeFactory

    return CountryOfficeFactory()


@pytest.fixture()
def user_role(request, db):
    from testutils.factories import CountryOfficeFactory, UserFactory, UserRoleFactory

    from hope_country_report.apps.core.utils import get_or_create_reporter_group

    if "country_office" in request.fixturenames:
        co = request.getfixturevalue("country_office")
    else:
        co: "CountryOffice" = CountryOfficeFactory()

    if "u" in request.fixturenames:
        user = request.getfixturevalue(request.getfixturevalue("u"))
    # elif "admin_user" in request.fixturenames:
    #     user = request.getfixturevalue("admin_user")
    # elif "user" in request.fixturenames:
    #     user = request.getfixturevalue("user")
    # elif "anonymous" in request.fixturenames:
    #     user = request.getfixturevalue("anonymous")
    else:
        user = UserFactory()
    if user.is_anonymous:
        return None
    g: "Group" = get_or_create_reporter_group()
    r: "UserRole" = UserRoleFactory(group=g, user=user, country_office=co)
    return r


@contextlib.contextmanager
def active_tenant(tenant: "CountryOffice"):
    from tenant_admin.config import conf

    current = conf.strategy.get_selected_tenant()
    if tenant:
        conf.strategy._selected_tenant = tenant
    yield
    conf.strategy._selected_tenant = current


@pytest.mark.parametrize("u", ["user", "admin_user", "anonymous"])
def test_tenant_backend_get_all_permissions(request, country_office, req, u, user_role, django_assert_max_num_queries):
    from tenant_admin.auth import BaseTenantAuth

    req.user = request.getfixturevalue(u)
    b: BaseTenantAuth = BaseTenantAuth()
    if hasattr(req.user, "_tenant_%s_perm_cache" % country_office.pk):
        delattr(req.user, "_tenant_%s_perm_cache" % country_office.pk)

    with active_tenant(country_office):
        with django_assert_max_num_queries(1):
            if req.user.is_authenticated:
                assert b.get_all_permissions(req.user)
                with django_assert_max_num_queries(0):
                    assert b.get_all_permissions(req.user)
            else:
                assert not b.get_all_permissions(req.user)
                with django_assert_max_num_queries(0):
                    assert not b.get_all_permissions(req.user)


@pytest.mark.parametrize("u", ["user", "admin_user"])
def test_tenant_backend_get_all_permissions_no_tenant(
    request, country_office, req, u, user_role, django_assert_max_num_queries
):
    from tenant_admin.auth import BaseTenantAuth

    req.user = request.getfixturevalue(u)
    b: BaseTenantAuth = BaseTenantAuth()
    if hasattr(req.user, "_tenant_%s_perm_cache" % country_office.pk):
        delattr(req.user, "_tenant_%s_perm_cache" % country_office.pk)

    with django_assert_max_num_queries(1):
        assert not b.get_all_permissions(req.user)


#
#
# def test_tenant_backend_no_active_tenant(db, req):
#     from testutils.factories import CountryOfficeFactory, UserRoleFactory
#
#     from hope_country_report.apps.core.utils import get_or_create_reporter_group
#     from hope_country_report.apps.tenant.auth import BaseTenantAuth
#
#     g: "Group" = get_or_create_reporter_group()
#     co: "CountryOffice" = CountryOfficeFactory()
#     r: "UserRole" = UserRoleFactory(group=g, user=req.user, country_office=co)
#     b: BaseTenantAuth = BaseTenantAuth()
#     assert b.get_all_permissions(req) == []
#
#


#
# def test_tenant_backend_active_tenant(db, req):
#     from testutils.factories import CountryOfficeFactory, UserFactory, UserRoleFactory
#
#     from hope_country_report.apps.core.utils import get_or_create_reporter_group
#     from hope_country_report.apps.tenant.auth import BaseTenantAuth
#
#     co: "CountryOffice" = CountryOfficeFactory()
#     with active_tenant(co):
#         g: "Group" = get_or_create_reporter_group()
#         r: "UserRole" = UserRoleFactory(group=g, user=req.user, country_office=co)
#         b: BaseTenantAuth = BaseTenantAuth()
#         assert b.get_all_permissions(req) != []
#
#
# def test_tenant_backend_superuser(db, req, admin_user):
#     from testutils.factories import CountryOfficeFactory
#
#     from hope_country_report.apps.tenant.auth import BaseTenantAuth
#
#     assert req.user.is_superuser
#     assert state.request.user.is_superuser
#     co: "CountryOffice" = CountryOfficeFactory()
#     with active_tenant(co):
#         b: BaseTenantAuth = BaseTenantAuth()
#         assert b.get_all_permissions(req) != []
#
#
# @pytest.mark.parametrize("u", ["user", "admin_user", "anonymous"])
# def test_tenant_backend_get_allowed_tenants(db, request, u, req):
#     from testutils.factories import CountryOfficeFactory
#
#     from hope_country_report.apps.tenant.auth import BaseTenantAuth
#     from testutils.factories import UserRoleFactory
#     from hope_country_report.apps.core.utils import get_or_create_reporter_group
#
#     user = request.getfixturevalue(u)
#     req.user = user
#     b: BaseTenantAuth = BaseTenantAuth()
#     if user.is_authenticated:
#         co: "CountryOffice" = CountryOfficeFactory()
#         g: "Group" = get_or_create_reporter_group()
#         r: "UserRole" = UserRoleFactory(group=g, user=req.user, country_office=co)
#         assert b.get_allowed_tenants().values_list("pk", flat=True)
#     else:
#         assert not b.get_allowed_tenants().values_list("pk", flat=True)
#
# @pytest.mark.parametrize("u", ["user", "admin_user", "anonymous"])
# def test_tenant_backend_has_module_perms(request, country_office, req, u, user_role, django_assert_max_num_queries):
#     from tenant_admin.auth import BaseTenantAuth
#
#     req.user = request.getfixturevalue(u)
#     b: BaseTenantAuth = BaseTenantAuth()
#     if hasattr(req.user, "_tenant_%s_perm_cache" % country_office.pk):
#         delattr(req.user, "_tenant_%s_perm_cache" % country_office.pk)
#     with active_tenant(country_office):
#         with django_assert_max_num_queries(1):
#             if req.user.is_authenticated:
#                 assert b.has_module_perms(req, "hope")
#             else:
#                 assert not b.has_module_perms(req, "hope")
#
#     with django_assert_max_num_queries(1):
#         assert not b.has_module_perms(req, "hope")


@pytest.mark.parametrize("u", ["user", "admin_user", "anonymous"])
def test_tenant_backend_get_allowed_tenants(request, country_office, req, u, user_role, django_assert_max_num_queries):
    from tenant_admin.auth import BaseTenantAuth

    req.user = request.getfixturevalue(u)
    b: BaseTenantAuth = BaseTenantAuth()

    # with django_assert_max_num_queries(1):
    if req.user.is_authenticated:
        assert list(b.get_allowed_tenants().values_list("pk", flat=True)) == [country_office.pk]
    else:
        assert not b.get_allowed_tenants().values_list("pk", flat=True)
