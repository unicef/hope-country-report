import logging
from typing import TYPE_CHECKING, Any

from django.utils.translation import gettext_lazy

from hope_country_report.apps.tenant.forms import TenantAuthenticationForm
from hope_country_report.apps.tenant.sites import TenantAdminSite
from hope_country_report.apps.tenant.utils import get_selected_tenant, must_tenant

if TYPE_CHECKING:
    from django.http import HttpRequest
    from django.utils.functional import _StrOrPromise

logger = logging.getLogger(__name__)


class HRAdminSite(TenantAdminSite):
    site_title: "_StrOrPromise" = gettext_lazy("HOPE Reporting site admin")
    # site_header = gettext_lazy("HOPE Reporting administration")
    index_title: "_StrOrPromise" = gettext_lazy("=")
    login_form = TenantAuthenticationForm

    @property
    def site_header(self) -> "_StrOrPromise":
        if must_tenant():
            return gettext_lazy("HOPE Reporting %s") % (get_selected_tenant() or "")
        return gettext_lazy("HOPE Reporting")

    # def each_context(self, request: "AuthHttpRequest") -> "Dict[str, Any]":
    #     ret = super().each_context(request)
    #     ret["available_apps"] = self.get_app_list(request)
    #     return ret

    def _build_app_dict(self, request: "HttpRequest", label: "_StrOrPromise|None" = None) -> dict[str, Any]:
        app_dict = super()._build_app_dict(request, label)
        for data in app_dict.values():
            data["models"] = [m for m in data["models"] if not hasattr(m, "Tenant")]
        return app_dict
