from functools import update_wrapper
from typing import Callable, TYPE_CHECKING

from django.http import HttpResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse, URLPattern, URLResolver

from smart_admin.site import SmartAdminSite

from hope_country_report.state import state

from .config import conf
from .exceptions import TenantAdminError
from .forms import SelectTenantForm, TenantAuthenticationForm
from .resolver import tenant_patterns
from .utils import replace_tenant
from .views import set_tenant

if TYPE_CHECKING:
    from typing import Any, Dict

    from hope_country_report.types.http import AuthHttpRequest


class TenantAdminSite(SmartAdminSite):
    index_title = site_header = site_title = "HOPE Reporting"
    enable_nav_sidebar = False
    smart_index_template = "tenant_admin/smart_index.html"
    app_index_template = "tenant_admin/app_index.html"
    index_template = "tenant_admin/index.html"
    login_template = "tenant_admin/login.html"
    login_form = TenantAuthenticationForm

    def __init__(self, name: str = "tenant_admin") -> None:
        super().__init__(name)

    def has_permission(self, request):
        """
        Return True if the given HttpRequest has permission to view
        *at least one* page in the admin site.
        """
        return request.user.is_active

    def each_context(self, request: "AuthHttpRequest") -> "Dict[str, Any]":
        ret = super().each_context(request)
        selected_tenant = conf.strategy.get_selected_tenant(request)
        ret["tenant_form"] = SelectTenantForm(initial={"tenant": selected_tenant}, request=request)
        ret["current_app"] = self.name
        return ret  # type: ignore

    def is_smart_enabled(self, request):
        return False

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

        urlpatterns = [
            path("", wrap(self.index), name="index"),
            path("login/", self.login, name="login"),
            path("logout/", self.logout, name="logout"),
            path("select/", wrap(self.select_tenant), name="select_tenant"),
        ]
        urlpatterns += [
            *tenant_patterns(*super().get_urls()),
        ]

        return urlpatterns

    @property
    def urls(self) -> "tuple[list[URLResolver | URLPattern], str, str]":
        if not self._registry:
            from tenant_admin.options import model_admin_registry

            for m, a in model_admin_registry.items():
                self.register(m, a)
        return self.get_urls(), "tenant_admin", "tenant_admin"

    def _build_app_dict(self, request, label=None):
        original = super()._build_app_dict(request, label)
        for app_label, data in original.items():
            original[app_label]["app_url"] = "#"
            for mdata in data["models"]:
                model = mdata["model"]
                info = (app_label, model._meta.model_name)
                if mdata["admin_url"]:
                    tenant_url = reverse("tenant_admin:%s_%s_changelist" % info, current_app="tenant_admin")
                    mdata["admin_url"] = replace_tenant(tenant_url, state.tenant)
                # mdata["name"] += f"  {state.tenant} {mdata['admin_url']}"
        return original

    # @method_decorator(never_cache)
    # def login(self, request, extra_context=None):
    #     if request.method == "GET" and self.has_permission(request):
    #         # Already logged-in, redirect to admin index
    #         index_path = reverse("tenant_admin:select_tenant", current_app=self.name)
    #         return HttpResponseRedirect(index_path)
    #     # Since this module gets imported in the application's root package,
    #     # it cannot import models from other applications at the module level,
    #     # and django.contrib.admin.forms eventually imports User.
    #     from django.contrib.admin.forms import AdminAuthenticationForm
    #     from django.contrib.auth.views import LoginView
    #
    #     context = {
    #         **self.each_context(request),
    #         "title": "Log in ",
    #         "subtitle": None,
    #         "app_path": request.get_full_path(),
    #         "username": request.user.get_username(),
    #     }
    #     if REDIRECT_FIELD_NAME not in request.GET and REDIRECT_FIELD_NAME not in request.POST:
    #         context[REDIRECT_FIELD_NAME] = reverse("tenant_admin:select_tenant", current_app=self.name)
    #     context.update(extra_context or {})
    #
    #     defaults = {
    #         "extra_context": context,
    #         "authentication_form": self.login_form or AdminAuthenticationForm,
    #         "template_name": self.login_template or "tenant_admin/login.html",
    #     }
    #     request.current_app = self.name
    #     return LoginView.as_view(**defaults)(request)

    def index(self, request: "AuthHttpRequest", extra_context: "Dict|None" = None) -> "HttpResponse":
        """
        Display the main admin index page, which lists all of the installed
        apps that have been registered in this site.
        """
        if not conf.strategy.get_selected_tenant(request):
            return redirect(f"{self.name}:select_tenant")
        app_list = self.get_app_list(request)
        context = {
            **self.each_context(request),
            "title": self.index_title,
            "tenant": conf.strategy.get_selected_tenant(request),
            "subtitle": None,
            "app_list": app_list,
            **(extra_context or {}),
        }

        request.current_app = self.name

        return TemplateResponse(request, self.index_template, context)

    def select_tenant(self, request: "AuthHttpRequest") -> "HttpResponse":
        context = self.each_context(request)
        if request.method == "POST":
            form = SelectTenantForm(request.POST, request=request)
            if form.is_valid():
                response = set_tenant(request)
                return response

        form = SelectTenantForm(request=request, initial={"next": "/"})
        context["form"] = form
        return TemplateResponse(request, "tenant_admin/select_tenant.html", context)
