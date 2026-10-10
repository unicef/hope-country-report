from typing import TYPE_CHECKING

import pytest
from django.test import override_settings
from django.urls import reverse

from hope_country_report.state import state

if TYPE_CHECKING:
    from hope_country_report.apps.core.models import CountryOffice

pytestmark = pytest.mark.django_db()


@override_settings(LOGIN_ENABLED=True)
def test_login_admnin(django_app, admin_user):
    url = reverse("admin:login")
    res = django_app.get(url)
    form = res.forms[0]
    form["username"] = admin_user.username
    form["password"] = "password"
    res = form.submit()
    assert res.status_code == 302
    assert res.location == "/admin/"


@override_settings(LOGIN_ENABLED=True)
def test_login_tenant_user(django_app, tenant_user):
    tenant_user.is_staff = True
    tenant_user.save(update_fields=["is_staff"])
    tenant: "CountryOffice" = tenant_user.roles.first().country_office
    res = django_app.get(reverse("admin:login"))
    form = res.forms[0]
    form["username"] = tenant_user.username
    form["password"] = "password"
    res = form.submit()
    assert res.status_code == 302, res.context["form"].errors
    assert res.location == "/admin/"
    res = res.follow()  # -> /admin/+select/
    res = res.follow()  # -> tenant selection page
    res.forms["select-tenant"]["tenant"] = tenant.pk
    res = res.forms["select-tenant"].submit().follow()
    assert res.pyquery("#site-name a").text() == f"HOPE Reporting {tenant.name}"
    assert state.tenant is None


@override_settings(LOGIN_ENABLED=True)
def test_login_pending_user(django_app, pending_user):
    pending_user.is_staff = True
    pending_user.save(update_fields=["is_staff"])
    res = django_app.get(reverse("admin:login"))
    form = res.forms[0]
    form["username"] = pending_user.username
    form["password"] = "password"
    res = form.submit()
    assert res.status_code == 302, res.context["form"].errors
    assert res.location == "/admin/"
    res = res.follow()  # -> /admin/+select/
    res = res.follow()  # -> tenant selection page
    assert b"Seems you do not have any tenant enabled." in res.body
