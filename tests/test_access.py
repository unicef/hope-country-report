from typing import TYPE_CHECKING

from django.urls import reverse

if TYPE_CHECKING:
    from hope_country_report.apps.core.models import CountryOffice


def test_login_admnin(django_app, admin_user):
    url = reverse("admin:login")
    res = django_app.get(url)
    res.form["username"] = admin_user.username
    res.form["password"] = admin_user.password
    res = res.form.submit()
    assert res.status_code == 302
    assert res.location == "/"


def test_login_tenant_user(django_app, tenant_user):
    select_tenant_url = reverse("admin:select_tenant")
    url = reverse("admin:login")
    res = django_app.get(url)
    res.form["username"] = tenant_user.username
    res.form["password"] = tenant_user.password
    res = res.form.submit()
    assert res.status_code == 302, res.context["form"].errors
    assert res.location == select_tenant_url
    res = res.follow()
    tenant: "CountryOffice" = tenant_user.roles.first().country_office
    res.forms["select-tenant"]["tenant"] = tenant.pk
    res = res.forms["select-tenant"].submit().follow()
    res.showbrowser()
    assert res.pyquery("#site-name a").text() == "HOPE Reporting %s" % tenant.name
