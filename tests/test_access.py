from typing import TYPE_CHECKING

import pytest

from django.test import override_settings
from django.urls import reverse

from hope_country_report.state import state

if TYPE_CHECKING:
    from hope_country_report.apps.core.models import CountryOffice

pytestmark = pytest.mark.django_db()


# pytestmark = pytest.mark.django_db(databases=["default", "hope_ro"])


@override_settings(LOGIN_ENABLED=True)
def test_login_admnin(django_app, admin_user):
    url = reverse("admin:login")
    res = django_app.get(url)
    res.form["username"] = admin_user.username
    res.form["password"] = "password"
    res = res.form.submit()
    assert res.status_code == 200
    assert res.location == "/admin/"


@override_settings(LOGIN_ENABLED=True)
def test_login_tenant_user(django_app, tenant_user):
    tenant: "CountryOffice" = tenant_user.roles.first().country_office
    select_tenant_url = reverse("admin:select_tenant")
    res = django_app.get(reverse("admin:login"))
    res.form["username"] = tenant_user.username
    res.form["password"] = "password"
    res = res.form.submit()
    assert res.status_code == 302, res.context["form"].errors
    assert res.location == select_tenant_url
    res = res.follow()
    res.forms["select-tenant"]["tenant"] = tenant.pk
    res = res.forms["select-tenant"].submit().follow()
    assert res.pyquery("#site-name a").text() == f"HOPE Reporting {tenant.name}"
    assert state.tenant is None


@override_settings(LOGIN_ENABLED=True)
def test_login_pending_user(django_app, pending_user):
    select_tenant_url = reverse("admin:select_tenant")
    res = django_app.get(reverse("admin:login"))
    res.form["username"] = pending_user.username
    res.form["password"] = "password"
    res = res.form.submit()
    assert res.status_code == 302, res.context["form"].errors
    assert res.location == select_tenant_url
    res = res.follow()
    assert b"Seems you do not have any tenant enabled." in res.body
