import logging
from typing import TYPE_CHECKING

from hope_country_report.apps.hope.models import BusinessArea
from tenant_admin.strategy import BaseTenantStrategy

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from hope_country_report.types.http import AuthHttpRequest

logger = logging.getLogger(__name__)


class Strategy(BaseTenantStrategy):
    def get_allowed_tenants(self, request: "AuthHttpRequest") -> "QuerySet[BusinessArea]":
        # if request.user.is_authenticated:
        #     return BusinessArea.objects.filter(id__in=request.user.userrole.values_list("business_area", flat=True))
        # else:
        return BusinessArea.objects.all()

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
