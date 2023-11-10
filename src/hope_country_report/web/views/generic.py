from typing import Any, TYPE_CHECKING, TypeVar

import datetime
from urllib.parse import urlparse

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Model
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, StreamingHttpResponse
from django.shortcuts import redirect, render
from django.urls import resolve, reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView, TemplateView, UpdateView

import django_stubs_ext
from djgeojson.templatetags.geojson_tags import geojsonfeature

from hope_country_report.apps.core.forms import CountryOfficeForm
from hope_country_report.apps.core.models import CountryOffice, User
from hope_country_report.apps.tenant.forms import SelectTenantForm
from hope_country_report.apps.tenant.utils import set_selected_tenant
from hope_country_report.utils.media import download_media

from .base import SelectedOfficeMixin

django_stubs_ext.monkeypatch()

if TYPE_CHECKING:
    from django.core.paginator import _SupportsPagination
    from django.db.models import QuerySet
    from django.views.generic.edit import _ModelFormT

    _M = TypeVar("_M", bound=Model, covariant=True)


@login_required
def index(request: "HttpRequest") -> "HttpResponse":
    return redirect("select-tenant")


#
# class SelectedOfficeMixin(LoginRequiredMixin, View):
#     @cached_property
#     def selected_office(self) -> CountryOffice:
#         if self.request.user.is_superuser:
#             co = CountryOffice.objects.get(slug=self.kwargs["co"])
#         else:
#             co = CountryOffice.objects.filter(userrole__user=self.request.user, slug=self.kwargs["co"])[0]
#         return co
#
#     def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
#         kwargs["view"] = self
#         kwargs["view_name"] = self.__class__.__name__
#         kwargs["selected_office"] = self.selected_office
#         kwargs["tenant_form"] = SelectTenantForm(request=self.request, initial={"tenant": self.selected_office})
#         return super().get_context_data(**kwargs)
#
#     def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse | StreamingHttpResponse:
#         response = super().get(request, *args, **kwargs)
#         signer = get_cookie_signer()
#         response.set_cookie(conf.COOKIE_NAME, signer.sign(self.selected_office.slug))
#         return response
#


class OfficePreferencesView(SelectedOfficeMixin, PermissionRequiredMixin, UpdateView[CountryOffice, Any]):
    template_name = "web/office/prefs.html"
    permission_required = ["core.change_countryoffice"]
    model = CountryOffice
    form_class = CountryOfficeForm
    success_url = "."

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        from django.utils import formats
        from django.utils.translation import override

        sample = datetime.datetime(2000, 12, 31, 23, 59)

        with override(self.get_object().locale):
            return super().get_context_data(
                aaa=formats.date_format(sample),
                bbb=formats.time_format(sample),
                ccc=formats.number_format(12345678),
                ddd=formats.number_format(123.45),
                **kwargs,
            )

    def get_object(self, queryset: "QuerySet[_M] | None" = None) -> "CountryOffice":
        return self.selected_office

    def form_valid(self, form: "_ModelFormT") -> "HttpResponse":
        response = super().form_valid(form)
        messages.success(self.request, _("Saved."))
        return response


class OfficeHomeView(SelectedOfficeMixin, TemplateView):
    template_name = "web/office/index.html"


#
# class OfficeTemplateView(SelectedOfficeMixin, TemplateView):
#     template_name = "web/office/index.html"


class OfficeMapView(SelectedOfficeMixin, TemplateView):
    template_name = "web/office/map.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        return super().get_context_data(
            aaa={
                "DEFAULT_ZOOM": 13,
                # "MIN_ZOOM": 12,
                "MAX_ZOOM": 13,
                "DEFAULT_CENTER": [self.selected_office.shape.lat, self.selected_office.shape.lon],
            },
            feature=mark_safe(geojsonfeature(self.selected_office.shape, ":mpoly")),
            **kwargs,
        )


class OfficeUserListView(SelectedOfficeMixin, ListView[User]):
    template_name = "web/office/users.html"

    def get_queryset(self) -> "_SupportsPagination[_M]":
        qs = User.objects.filter(roles__country_office=self.selected_office)
        return qs


class OfficePageListView(SelectedOfficeMixin, ListView[User]):
    template_name = "web/office/pages.html"

    def get_queryset(self) -> "_SupportsPagination[_M]":
        qs = User.objects.filter(roles__country_office=self.selected_office)
        return qs


@login_required
def download(request: "HttpRequest", path: str) -> HttpResponse | StreamingHttpResponse:
    return download_media(path)


@login_required
def select_tenant(request: "HttpRequest") -> "HttpResponse":
    if request.method == "POST":
        form = SelectTenantForm(request.POST, request=request)
        if form.is_valid():
            office = form.cleaned_data["tenant"]
            set_selected_tenant(form.cleaned_data["tenant"])
            try:
                resolver = resolve(urlparse(request.META.get("HTTP_REFERER", "/")).path)
                if list(resolver.kwargs.keys()) == ["co"]:
                    return HttpResponseRedirect(reverse(resolver.url_name, args=[office.slug]))
                else:
                    raise Exception(resolver)
            except Exception:
                pass
            return HttpResponseRedirect(reverse("office-index", args=[office.slug]))
    else:
        return render(request, "select_tenant.html", {"tenant_form": SelectTenantForm(request=request)})
