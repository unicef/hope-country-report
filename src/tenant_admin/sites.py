from functools import update_wrapper
from typing import Any, Dict, Optional

from django.contrib.admin import ModelAdmin
from django.core.signing import Signer
from django.db.models import Model
from django.http import HttpRequest
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from smart_admin.site import SmartAdminSite

from .config import conf
from .exceptions import InvalidTenantError, TenantAdminError
from .forms import SelectTenantForm, TenantAuthenticationForm
from .options import TenantModelAdmin

signer = Signer()


class TenantAdminSite(SmartAdminSite):
    site_title = "Control Panel"
    site_header = "Control Panel"
    index_title = "Control Panel"
    enable_nav_sidebar = False
    login_form = TenantAuthenticationForm
    index_template = "tenant_admin/index.html"
    smart_index_template = "tenant_admin/smart_index.html"

    ba_cookie_name = "selected_ba"
    app_index_template = "tenant_admin/app_index.html"

    def __init__(self, name="tenant_admin") -> None:
        super().__init__(name)
        from .options import model_admin_registry

        for opt in model_admin_registry:
            self.register(opt)

    def reverse(self, name):
        return reverse(f"{self.name}:{name}")

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

    def login(self, request, extra_context=None):
        return super().login(request, extra_context)

    def get_smart_settings(self, request):
        return {"BOOKMARKS": [], "ANYUSER_LOG": True}

    def index(self, request, extra_context=None):
        if not conf.strategy.get_selected_tenant(request):
            return redirect(f"{self.name}:select_tenant")
        return super().index(request)


    def app_index(self, request, app_label, extra_context=None):
        if not conf.strategy.get_selected_tenant(request):
            return redirect(f"{self.name}:select_tenant")
        return super().app_index(request, app_label, extra_context)

    def get_selected_tenant(self, request: HttpRequest) -> Optional[Model]:
        try:
            return conf.strategy.get_selected_tenant(request)
        except InvalidTenantError:
            return None

    def each_context(self, request: HttpRequest) -> Dict[str, Any]:
        ret = super().each_context(request)
        selected_tenant = self.get_selected_tenant(request)
        # ret["bookmarks"] = []
        # ret["site_title"] = "site_title"
        ret["site_header"] = "%s Control Panel" % (selected_tenant or "")
        ret["site_name"] = self.name
        ret["site_url"] = "site_url"
        ret["selected_tenant"] = selected_tenant
        # ret["current_app"] = self.name
        ret["tenant_form"] = SelectTenantForm(
            initial={"tenant": selected_tenant}, request=request
        )
        return ret  # type: ignore

    def register(self, admin_class: TenantModelAdmin, **options: Any) -> None:
        self._registry[admin_class.model] = admin_class(admin_class.model, self)

    def has_permission(self, request: HttpRequest) -> bool:
        return request.user.is_active

    def is_smart_enabled(self, request: HttpRequest) -> bool:
        return False

    def get_tenant_modeladmin(self) -> ModelAdmin:
        return self._registry[conf.tenant_model]

    @property
    def urls(self):
        return self.get_urls(), 'admin', self.name


site: TenantAdminSite = TenantAdminSite()
