import logging
from typing import TYPE_CHECKING

from django.core.exceptions import ObjectDoesNotExist
from django.core.signing import get_cookie_signer
from django.http import HttpResponse
from django.utils.functional import cached_property

# FIXME: this should be DIP
from hope_country_report.state import state

from .config import AppSettings

if TYPE_CHECKING:
    from hope_country_report.types.django import _M, _R

    from .backend import TenantBackend

logger = logging.getLogger(__name__)


class BaseTenantStrategy:
    pk = "pk"

    def __init__(self, config: AppSettings):
        self.config = config
        self._selected_tenant: "_M|None" = None
        self._selected_tenant_value = ""

    def set_selected_tenant(self, instance: "_M", response: "HttpResponse|None" = None) -> None:
        self._selected_tenant = instance
        if response:
            signer = get_cookie_signer()
            response.set_cookie(self.config.COOKIE_NAME, signer.sign(getattr(instance, self.pk)))

    @cached_property
    def auth(self) -> "TenantBackend":
        return self.config.auth

    #
    # def get_tenant_filter(self, model_admin: "BaseTenantModelAdmin", request: "_R"):
    #     if not model_admin.tenant_filter_field:
    #         raise ValueError(
    #             f"Set 'tenant_filter_field' on {self} or override `get_queryset()` to enable queryset filtering"
    #         )
    #     if model_admin.tenant_filter_field == "__none__":
    #         return {}
    #     active_tenant = self.get_selected_tenant(request)
    #     if not active_tenant:
    #         raise InvalidTenantError
    #     return {model_admin.tenant_filter_field: active_tenant.hope_id}

    # def read_selected_tenant(self, request: "_R|None" = None) -> "_M | None":
    #     self._selected_tenant = None
    #     from django.urls import resolve
    #
    #     args = resolve(request.path)
    #     request = request or state.request
    #     # if request:
    #     #     signer = get_cookie_signer()
    #     #     cookie_value = request.COOKIES.get(self.config.COOKIE_NAME)
    #     #     if cookie_value:
    #     #         try:
    #     #             filters = {self.pk: signer.unsign(cookie_value)}
    #     #             self._selected_tenant_value = cookie_value
    #     #             self._selected_tenant = self.auth.get_allowed_tenants().get(**filters)
    #     #         except (ValueError, ObjectDoesNotExist):
    #     #             self._selected_tenant = None
    #     #         # except TypeError:
    #     #         #     self._selected_tenant = None
    #     #         except Exception as e:  # pragma: no cover
    #     #             logger.exception(e)
    #     #             raise
    #     return self._selected_tenant

    def get_selected_tenant(self, request: "_R|None" = None) -> "_M | None":
        # if self._selected_tenant is NONE:
        #     self.read_selected_tenant(request)
        request = request or state.request
        if request.user.is_authenticated and state.tenant:
            try:
                filters = {"slug": state.tenant}
                return self.auth.get_allowed_tenants().get(**filters)
            except ObjectDoesNotExist:
                return None
        return self._selected_tenant


class TenantStrategy(BaseTenantStrategy):
    pass
    # def get_allowed_tenants(self, request: "AuthHttpRequest") -> "QuerySet[BusinessArea]":
    #     # if request.user.is_authenticated:
    #     #     return BusinessArea.objects.filter(id__in=request.user.userrole.values_list("business_area", flat=True))
    #     # else:
    #     return CountryOffice.objects.order_by("name")

    # def get_selected_tenant(self, request: "R") -> "M | None":
    #     cookie_value: str = str(request.COOKIES.get(self.config.COOKIE_NAME))
    #     signer = get_cookie_signer()
    #     if (self._selected_tenant_value != cookie_value) or (self._selected_tenant is None):
    #         try:
    #             filters = {str(self.pk): signer.unsign(str(cookie_value))}
    #             self._selected_tenant_value = cookie_value
    #             self._selected_tenant = self.config.auth.get_allowed_tenants(request).get(**filters)
    #         except ObjectDoesNotExist:
    #             self._selected_tenant = None
    #         except TypeError:
    #             self._selected_tenant = None
    #         except Exception as e:  # pragma: no cover
    #             logger.exception(e)
    #             self._selected_tenant = None
    #     state.tenant = self._selected_tenant
    #     return self._selected_tenant  # type: ignore[return-value]
