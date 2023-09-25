from functools import update_wrapper
from typing import TYPE_CHECKING

from django.shortcuts import redirect
from django.template.response import TemplateResponse

from smart_admin.site import SmartAdminSite

from .config import conf
from .exceptions import TenantAdminError
from .forms import SelectTenantForm
from .options import TenantModelAdmin

if TYPE_CHECKING:
    from hope_country_report.types.tenant import _T


class TenantAdminSite(SmartAdminSite):
    index_title = site_header = site_title = "HOPE Reporting"
    enable_nav_sidebar = False
    smart_index_template = "tenant_admin/smart_index.html"
    index_template = "tenant_admin/index.html"

    def __init__(self, name="tenant_admin") -> None:
        super().__init__(name)

    def each_context(self, request: "HttpRequest") -> "Dict[str, Any]":
        ret = super().each_context(request)
        selected_tenant = conf.strategy.get_selected_tenant(request)
        ret["tenant_form"] = SelectTenantForm(initial={"tenant": selected_tenant}, request=request)
        return ret  # type: ignore

    def get_urls(self):
        from django.urls import path

        def wrap(view, cacheable=False):
            def wrapper(*args, **kwargs):
                try:
                    return self.admin_view(view, cacheable)(*args, **kwargs)
                except TenantAdminError:
                    return redirect(f"{self.name}:select_tenant")

            wrapper.admin_site = self
            return update_wrapper(wrapper, view)

        urlpatterns = [path("select/", wrap(self.select_tenant), name="select_tenant")]
        urlpatterns += super().get_urls()

        return urlpatterns

    @property
    def urls(self):
        return self.get_urls(), "tenant_admin", self.name

    def index(self, request, extra_context=None):
        if not conf.strategy.get_selected_tenant(request):
            return redirect(f"{self.name}:select_tenant")
        return super().index(request)

    def select_tenant(self, request):
        context = self.each_context(request)
        if request.method == "POST":
            form = SelectTenantForm(request.POST, request=request)
            if form.is_valid():
                if "next" in request.GET:
                    response = redirect(request.GET["next"])
                else:
                    response = redirect(f"{self.name}:index")
                conf.strategy.set_selected_tenant(response, form.cleaned_data["tenant"])
                return response
        form = SelectTenantForm(request=request)
        context["form"] = form
        return TemplateResponse(request, "tenant_admin/select_tenant.html", context)


def add_to_site(*models):
    for m in models:
        name = m._meta.model_name.title()
        attrs = {
            "model": m,
        }
        MAdmin: "_T" = type(f"{name}Admin", (TenantModelAdmin,), attrs)
        # site.register(MAdmin)
