import logging
from functools import lru_cache
from typing import TYPE_CHECKING

from django.core.signing import get_cookie_signer

from hope_country_report.apps.tenant.config import conf
from hope_country_report.apps.tenant.exceptions import InvalidTenantError
from hope_country_report.state import state

if TYPE_CHECKING:
    from hope_country_report.types.django import _M

logger = logging.getLogger(__name__)


@lru_cache(1)
def get_selected_tenant() -> "_M | None":
    if state.tenant:
        filters = {"slug": state.tenant}
        state.filters.append(filters)
        return conf.auth.get_allowed_tenants().filter(**filters).first()
    return None


def is_tenant_valid() -> bool:
    return bool(get_selected_tenant())


def ensure_tenant():
    if not get_selected_tenant():
        raise InvalidTenantError


def is_tenant_active() -> bool:
    if state.request is None:
        return False
    if state.request.user.is_anonymous:
        return False
    if state.request.user.is_superuser:
        return False
    if state.request.user.roles.exists():
        return True
    # if state.request.user.is_staff:
    #     return False
    return True


def get_tenant_from_request(request):
    signer = get_cookie_signer()
    cookie_value = request.COOKIES.get(conf.COOKIE_NAME)
    if cookie_value:
        return signer.unsign(cookie_value)
