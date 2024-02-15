from typing import TYPE_CHECKING

from collections.abc import Callable
from functools import update_wrapper

from django.conf import settings
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse, URLPattern, URLResolver
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache

from smart_admin.autocomplete import SmartAutocompleteJsonView
from smart_admin.site import SmartAdminSite

from .forms import SelectTenantForm
from .utils import get_selected_tenant, is_tenant_valid, must_tenant, set_selected_tenant

if TYPE_CHECKING:
    from typing import Any, Dict

    from hope_country_report.types.http import AuthHttpRequest

    from ...types.django import AnyModel


class TenantAutocompleteJsonView(SmartAutocompleteJsonView):
    ...

    # def get_queryset(self):
    #     qs = super().get_queryset()
    #     qs = qs.filter(self.model_admin.model.objects.)
    #     return qs

    # def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
    #     return super().get_context_data(**kwargs)
    #
    def has_perm(self, request: "AuthHttpRequest", obj: "AnyModel|None" = None) -> bool:
        return request.user.is_active

    # def get(self, request, *args, **kwargs):
    #     return JsonResponse({"t": state.tenant.slug})


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
        ret["flower_address"] = settings.POWER_QUERY_FLOWER_ADDRESS
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

    def autocomplete_view(self, request: "AuthHttpRequest") -> HttpResponse:
        return TenantAutocompleteJsonView.as_view(admin_site=self)(request)

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
        if request.method == "POST":
            if request.user.is_authenticated and not request.user.is_staff:
                return HttpResponseRedirect(reverse("admin:select_tenant"))

        return response

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

    @method_decorator(never_cache)
    def select_tenant(self, request: "AuthHttpRequest") -> "HttpResponse":
        context = self.each_context(request)
        if request.method == "POST":
            form = SelectTenantForm(request.POST, request=request)
            if form.is_valid():
                set_selected_tenant(form.cleaned_data["tenant"])
                return HttpResponseRedirect("/admin/")

        form = SelectTenantForm(request=request, initial={"next": "/admin/"})
        context["form"] = form
        return TemplateResponse(request, "tenant_admin/select_tenant.html", context)
