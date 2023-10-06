import logging
from typing import Any, Dict, TYPE_CHECKING

from django.http import HttpRequest
from django.utils.translation import gettext_lazy

from hope_country_report.apps.tenant.forms import TenantAuthenticationForm
from hope_country_report.apps.tenant.sites import TenantAdminSite
from hope_country_report.apps.tenant.utils import get_selected_tenant, is_tenant_active

if TYPE_CHECKING:
    from django.utils.functional import _StrOrPromise

    from hope_country_report.types.http import AuthHttpRequest

logger = logging.getLogger(__name__)


class HRAdminSite(TenantAdminSite):
    site_title = gettext_lazy("HOPE Reporting site admin")
    # site_header = gettext_lazy("HOPE Reporting administration")
    index_title: "_StrPromise" = gettext_lazy("=")
    login_form = TenantAuthenticationForm

    @property
    def site_header(self) -> "_StrPromise":
        if is_tenant_active():
            return gettext_lazy("HOPE Reporting %s") % (get_selected_tenant() or "")
        return gettext_lazy("HOPE Reporting administration")

    def each_context(self, request: "AuthHttpRequest") -> "Dict[str, Any]":
        ret = super().each_context(request)
        ret["available_apps"] = self.get_app_list(request)
        return ret

    def _build_app_dict(self, request: "HttpRequest", label: "_StrOrPromise|None" = None) -> dict[str, Any]:
        app_dict = super()._build_app_dict(request, label)
        for k, data in app_dict.items():
            data["models"] = [m for m in data["models"] if not hasattr(m, "Tenant")]
        return app_dict
