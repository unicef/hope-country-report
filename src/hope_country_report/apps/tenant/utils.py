from typing import TYPE_CHECKING

import logging

from django.core.signing import get_cookie_signer

from hope_country_report.apps.tenant.config import conf
from hope_country_report.apps.tenant.exceptions import InvalidTenantError
from hope_country_report.state import state

if TYPE_CHECKING:
    from django.http import HttpResponse

    from hope_country_report.apps.core.models import CountryOffice
    from hope_country_report.types.http import AuthHttpRequest

logger = logging.getLogger(__name__)


def get_selected_tenant() -> "CountryOffice | None":
    if state.tenant_cookie and state.tenant is None:
        filters = {"slug": state.tenant_cookie}
        state.filters.append(filters)
        state.tenant = conf.auth.get_allowed_tenants().filter(**filters).first()
    return state.tenant


def set_selected_tenant(tenant: "CountryOffice") -> None:
    state.tenant = tenant
    state.add_cookies(conf.COOKIE_NAME, tenant.slug)


def is_tenant_valid() -> bool:
    return bool(get_selected_tenant())


def ensure_tenant() -> None:
    if not get_selected_tenant():
        raise InvalidTenantError


def must_tenant() -> bool:
    if state.must_tenant is None:
        if state.request is None:
            return False

        if state.request.user.is_anonymous:
            state.must_tenant = False
        elif state.request.user.is_superuser:
            state.must_tenant = False
        elif state.request.user.is_staff:
            state.must_tenant = False
        elif state.request.user.roles.exists():
            state.must_tenant = True
        else:
            state.must_tenant = None
    return state.must_tenant


def get_tenant_cookie_from_request(request: "AuthHttpRequest") -> str | None:
    if request and request.user.is_authenticated:
        if request.user.roles.exists():
            signer = get_cookie_signer()
            cookie_value = request.COOKIES.get(conf.COOKIE_NAME)
            if cookie_value:
                return signer.unsign(cookie_value)
    return None


class RequestHandler:
    def process_request(self, request: "AuthHttpRequest") -> None:
        state.reset()
        state.request = request
        state.tenant_cookie = get_tenant_cookie_from_request(request)
        state.tenant = get_selected_tenant()

    def process_response(self, request: "AuthHttpRequest", response: "HttpResponse|None") -> None:
        if response:
            state.set_cookies(response)
        state.reset()

    # @contextlib.contextmanager
    # def context(self, request: "AuthHttpRequest", response: "HttpResponse|None" = None) -> "Iterator[None]":
    #     self.process_request(request)
    #     yield
    #     self.process_response(request, response)
