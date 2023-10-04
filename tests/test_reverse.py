from typing import TYPE_CHECKING
from unittest import mock

from django.urls import reverse

from tenant_admin.utils import replace_tenant, TENANT_PREFiX

if TYPE_CHECKING:
    from django.test.client import RequestFactory

    from hope_country_report.apps.core.models import CountryOffice


# @pytest.fixture()
# def req(request: "FixtureRequest", rf: "RequestFactory") -> "AuthHttpRequest":
#     req: "AuthHttpRequest" = rf.get("/")
#     current = state.request
#     state.request = req
#     yield req
#     state.request = current


def test_reverse():
    url1 = reverse("admin:hope_household_changelist")
    url2 = reverse("tenant_admin:hope_household_changelist")
    assert url1 != url2


def test_resolver(rf: "RequestFactory", office: "CountryOffice"):
    req = rf.get(f"/co-{office.slug}/")
    with mock.patch("hope_country_report.state.state") as m:
        m.request = req
        m.tenant = office.slug
        url = replace_tenant(reverse("tenant_admin:hope_household_changelist"), office.slug)
        assert url == f"/{TENANT_PREFiX}{office.slug}/hope/household/"
