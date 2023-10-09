import logging
from typing import TYPE_CHECKING

from django.core.signing import get_cookie_signer

from hope_country_report.apps.core.models import CountryOffice
from hope_country_report.apps.tenant.config import conf
from hope_country_report.apps.tenant.exceptions import InvalidTenantError
from hope_country_report.state import state
from hope_country_report.utils.lru import lru_cache_not_none

if TYPE_CHECKING:
    from hope_country_report.types.django import AnyModel
    from hope_country_report.types.http import AuthHttpRequest

logger = logging.getLogger(__name__)


@lru_cache_not_none()
def get_selected_tenant() -> "AnyModel | None":
    if state.tenant and state.tenant_instance is None:
        filters = {"slug": state.tenant}
        state.filters.append(filters)
        state.tenant_instance = conf.auth.get_allowed_tenants().filter(**filters).first()
    return state.tenant_instance


def set_selected_tenant(tenant: "CountryOffice") -> None:
    state.tenant = tenant.slug
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
        elif state.request.user.is_anonymous:
            state.must_tenant = False
        elif state.request.user.is_superuser:
            state.must_tenant = False
        elif state.request.user.roles.exists():
            state.must_tenant = True
        else:
            state.must_tenant = True
    return state.must_tenant


def get_tenant_from_request(request: "AuthHttpRequest|None") -> str | None:
    if request and request.user.is_authenticated:
        if request.user.roles.exists():
            signer = get_cookie_signer()
            cookie_value = request.COOKIES.get(conf.COOKIE_NAME)
            if cookie_value:
                return signer.unsign(cookie_value)
    return None
