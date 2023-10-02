from functools import update_wrapper
from typing import Callable, TYPE_CHECKING

from django.http import HttpResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse

from smart_admin.site import SmartAdminSite

from .config import conf
from .exceptions import TenantAdminError
from .forms import SelectTenantForm

if TYPE_CHECKING:
    from typing import Any, Dict

    from django.urls import URLPattern, URLResolver

    from hope_country_report.types.http import AuthHttpRequest


class TenantAdminSite(SmartAdminSite):
    index_title = site_header = site_title = "HOPE Reporting"
    enable_nav_sidebar = False
    smart_index_template = "tenant_admin/smart_index.html"
    index_template = "tenant_admin/index.html"

    def __init__(self, name: str = "tenant_admin") -> None:
        super().__init__(name)

    def each_context(self, request: "AuthHttpRequest") -> "Dict[str, Any]":
        ret = super().each_context(request)
        selected_tenant = conf.strategy.get_selected_tenant(request)
        ret["tenant_form"] = SelectTenantForm(initial={"tenant": selected_tenant}, request=request)
        return ret  # type: ignore

    def get_urls(self) -> "list[URLResolver | URLPattern]":
        from django.urls import path

        urlpatterns: "list[URLResolver | URLPattern]"

        def wrap(view: "Callable[[Any], Any]", cacheable: bool = False) -> "Callable":
            def wrapper(*args, **kwargs):
                try:
                    return self.admin_view(view, cacheable)(*args, **kwargs)
                except TenantAdminError:
                    return redirect(f"{self.name}:select_tenant")

            wrapper.admin_site = self  # type: ignore
            return update_wrapper(wrapper, view)

        urlpatterns = [path("select/", wrap(self.select_tenant), name="select_tenant")]
        urlpatterns += super().get_urls()

        return urlpatterns

    @property
    def urls(self) -> "tuple[list[URLResolver | URLPattern], str, str]":
        return self.get_urls(), "tenant_admin", self.name

    def index(self, request: "AuthHttpRequest", extra_context: "Dict|None" = None) -> "HttpResponse":
        if not conf.strategy.get_selected_tenant(request):
            return redirect(f"{self.name}:select_tenant")
        return super().index(request)

    def select_tenant(self, request: "AuthHttpRequest") -> "HttpResponse":
        context = self.each_context(request)
        if request.method == "POST":
            form = SelectTenantForm(request.POST, request=request)
            if form.is_valid():
                if "next" in request.GET:
                    response = redirect(request.GET["next"])
                else:
                    response = redirect(f"{self.name}:index")
                conf.strategy.set_selected_tenant(form.cleaned_data["tenant"], response)
                return response
        form = SelectTenantForm(request=request)
        context["form"] = form
        return TemplateResponse(request, "tenant_admin/select_tenant.html", context)
