from functools import update_wrapper
from typing import Callable, TYPE_CHECKING

from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse, URLPattern, URLResolver
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache

from smart_admin.site import SmartAdminSite

from .forms import SelectTenantForm
from .utils import get_selected_tenant, is_tenant_valid, must_tenant, set_selected_tenant

if TYPE_CHECKING:
    from typing import Any, Dict

    from hope_country_report.types.http import AuthHttpRequest


class TenantAdminSite(SmartAdminSite):
    enable_nav_sidebar = False

    # smart_index_template = "tenant_admin/smart_index.html"
    # app_index_template = "tenant_admin/app_index.html"
    # index_template = "tenant_admin/index.html"
    # login_template = "tenant_admin/login.html"
    # login_form = TenantAuthenticationForm
    # template_dir = "tenant_admin"

    # def has_permission(self, request: "AuthHttpRequest") -> bool:
    #     return request.user.is_active

    def each_context(self, request: "AuthHttpRequest") -> "Dict[str, Any]":
        ret = super().each_context(request)
        if must_tenant():
            selected_tenant = get_selected_tenant()
            ret["tenant_form"] = SelectTenantForm(initial={"tenant": selected_tenant}, request=request)
            ret["active_tenant"] = selected_tenant
            # ret["tenant"] = selected_tenant
        else:
            ret["active_tenant"] = None
        return ret  # type: ignore

    def is_smart_enabled(self, request: "AuthHttpRequest") -> bool:
        if must_tenant():
            return False
        return super().is_smart_enabled(request)

    def has_permission(self, request: "AuthHttpRequest") -> bool:
        # if must_tenant():
        return request.user.is_active
        # return super().has_permission(request)

    def get_urls(self) -> "list[URLResolver | URLPattern]":
        from django.urls import path

        urlpatterns: "list[URLResolver | URLPattern]"

        def wrap(view: "Callable[[Any], Any]", cacheable: bool = False) -> "Callable[[Any], Any]":
            def wrapper(*args: "Any", **kwargs: "Any") -> "Callable[[], Any]":
                return self.admin_view(view, cacheable)(*args, **kwargs)

            wrapper.admin_site = self  # type: ignore
            return update_wrapper(wrapper, view)

        urlpatterns = [
            # path("", wrap(self.index), name="index"),
            # path("login/", self.login, name="login"),
            # path("logout/", self.logout, name="logout"),
            path("+select/", wrap(self.select_tenant), name="select_tenant"),
        ]
        urlpatterns += super().get_urls()
        # urlpatterns += [
        #     *tenant_patterns(*super().get_urls()),
        # ]

        return urlpatterns

    def login(
        self, request: "HttpRequest", extra_context: "dict[str, Any] | None" = None
    ) -> "HttpResponse|HttpResponseRedirect":
        response = super().login(request, extra_context)
        if request.method == "POST" and request.user.roles.exists():
            return HttpResponseRedirect(reverse("admin:select_tenant"))
        return response

    # @property
    # def urls(self) -> "tuple[list[URLResolver | URLPattern], str, str]":
    #     if not self._registry:
    #         from tenant_admin.options import model_admin_registry
    #
    #         for m, a in model_admin_registry.items():
    #             self.register(m, a)
    #     return self.get_urls(), "admin", "admin"

    # def _build_app_dict(self, request, label=None):
    #     original = super()._build_app_dict(request, label)
    #     for app_label, data in original.items():
    #         original[app_label]["app_url"] = "#"
    #         for mdata in data["models"]:
    #             model = mdata["model"]
    #             info = (app_label, model._meta.model_name)
    #             if mdata["admin_url"]:
    #                 tenant_url = reverse("tenant_admin:%s_%s_changelist" % info, current_app="tenant_admin")
    #                 mdata["admin_url"] = replace_tenant(tenant_url, state.tenant)
    #             # mdata["name"] += f"  {state.tenant} {mdata['admin_url']}"
    #     return original

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

    @method_decorator(never_cache)
    def index(
        self, request: "AuthHttpRequest", extra_context: "Dict[str,Any]|None" = None, **kwargs: "Any"
    ) -> "HttpResponse":
        """
        Display the main admin index page, which lists all of the installed
        apps that have been registered in this site.
        """
        if must_tenant() and not is_tenant_valid():
            return redirect(f"{self.name}:select_tenant")
        return super().index(request, extra_context, **kwargs)
        # app_list = self.get_app_list(request)
        # context = {
        #     **self.each_context(request),
        #     "title": self.index_title,
        #     "tenant": conf.strategy.get_selected_tenant(request),
        #     "subtitle": None,
        #     "app_list": app_list,
        #     **(extra_context or {}),
        # }
        #
        # request.current_app = self.name
        #
        # return TemplateResponse(request, self.index_template, context)

    @method_decorator(never_cache)
    def select_tenant(self, request: "AuthHttpRequest") -> "HttpResponse":
        if not must_tenant() and not is_tenant_valid():
            return redirect(f"{self.name}:index")
        context = self.each_context(request)
        if request.method == "POST":
            form = SelectTenantForm(request.POST, request=request)
            if form.is_valid():
                set_selected_tenant(form.cleaned_data["tenant"])
                return HttpResponseRedirect("/")

        form = SelectTenantForm(request=request, initial={"next": "/"})
        context["form"] = form
        return TemplateResponse(request, "tenant_admin/select_tenant.html", context)
