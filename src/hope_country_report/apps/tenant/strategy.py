import logging
from typing import TYPE_CHECKING

from django.core.signing import get_cookie_signer
from django.http import HttpResponse

from hope_country_report.apps.tenant.config import AppSettings

from .state import state

if TYPE_CHECKING:
    from hope_country_report.types.django import _M, _R

logger = logging.getLogger(__name__)


class BaseTenantStrategy:
    pk = "pk"

    def __init__(self, config: AppSettings):
        self.config = config
        self._selected_tenant: "_M|None" = None
        self._selected_tenant_value = ""

    def set_selected_tenant(self, response: "HttpResponse", instance: "_M") -> None:
        signer = get_cookie_signer()
        response.set_cookie(self.config.COOKIE_NAME, signer.sign(getattr(instance, self.pk)))

    def get_selected_tenant(self, request: "_R") -> "_M | None":
        cookie_value = request.COOKIES.get(self.config.COOKIE_NAME)
        signer = get_cookie_signer()
        if (self._selected_tenant_value != cookie_value) or (self._selected_tenant is None):
            try:
                filters = {self.pk: signer.unsign(cookie_value)}
                self._selected_tenant_value = cookie_value
                self._selected_tenant = self.config.auth.get_allowed_tenants(request).get(**filters)
            except ValueError:
                self._selected_tenant = None
            # except TypeError:
            #     self._selected_tenant = None
            except Exception as e:  # pragma: no cover
                logger.exception(e)
                raise
                # self._selected_tenant = None
        state.tenant = self._selected_tenant
        return self._selected_tenant


class Strategy(BaseTenantStrategy):
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
