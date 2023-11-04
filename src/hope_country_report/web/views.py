from typing import Any, TYPE_CHECKING, TypeVar

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import PermissionDenied
from django.core.signing import get_cookie_signer
from django.db.models import Model
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, StreamingHttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import DetailView, ListView, TemplateView, UpdateView
from django.views.generic.edit import FormView

import django_stubs_ext
from admin_extra_buttons.utils import HttpResponseRedirectToReferrer
from adminfilters.utils import parse_bool

from hope_country_report.apps.core.models import CountryOffice, User
from hope_country_report.apps.power_query.exceptions import RequestablePermissionDenied
from hope_country_report.apps.power_query.models import ReportConfiguration, ReportDocument
from hope_country_report.apps.tenant.config import conf
from hope_country_report.apps.tenant.forms import SelectTenantForm
from hope_country_report.apps.tenant.utils import set_selected_tenant
from hope_country_report.utils.mail import send_request_access
from hope_country_report.utils.media import download_media
from hope_country_report.web.forms import RequestAccessForm, UserProfileForm

django_stubs_ext.monkeypatch()

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractBaseUser
    from django.core.paginator import _SupportsPagination
    from django.db.models import QuerySet
    from django.views.generic.edit import _ModelFormT

    from hope_country_report.types.http import AuthHttpRequest, RedirectOrResponse

    _M = TypeVar("_M", bound=Model, covariant=True)


@login_required
def index(request: "HttpRequest") -> "HttpResponse":
    return redirect("select-tenant")
    # return render(request, "home.html", {"tenant_form": SelectTenantForm(request=request)})


class SelectedOfficeMixin(LoginRequiredMixin, View):
    @cached_property
    def selected_office(self) -> CountryOffice:
        if self.request.user.is_superuser:
            co = CountryOffice.objects.get(slug=self.kwargs["co"])
        else:
            # co = CountryOffice.objects.get(slug=self.kwargs["co"], userrole__user=self.request.user)
            co = CountryOffice.objects.get(slug=self.kwargs["co"])
        return co

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        kwargs["view"] = self
        kwargs["view_name"] = self.__class__.__name__
        kwargs["selected_office"] = self.selected_office
        kwargs["tenant_form"] = SelectTenantForm(request=self.request, initial={"tenant": self.selected_office})
        return super().get_context_data(**kwargs)

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse | StreamingHttpResponse:
        response = super().get(request, *args, **kwargs)
        signer = get_cookie_signer()
        response.set_cookie(conf.COOKIE_NAME, signer.sign(self.selected_office.slug))
        return response


class OfficeHomeView(SelectedOfficeMixin, TemplateView):
    template_name = "web/office/index.html"


class OfficeConfigurationListView(SelectedOfficeMixin, PermissionRequiredMixin, ListView[ReportConfiguration]):
    template_name = "web/office/config_list.html"
    permission_required = ["power_query.view_reportconfiguration"]

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        return super().get_context_data(title=_("Configured Reports"), **kwargs)

    def get_queryset(self) -> "_SupportsPagination[_M]":
        qs = ReportConfiguration.objects.filter(country_office=self.selected_office)
        if tag := self.request.GET.get("tag", None):
            qs = qs.filter(tags__name=tag)
        if active := self.request.GET.get("active", None):
            qs = qs.filter(active=parse_bool(active))
        return qs


class OfficeConfigurationDetailView(SelectedOfficeMixin, PermissionRequiredMixin, DetailView[ReportConfiguration]):
    template_name = "web/office/config.html"
    permission_required = ["power_query.view_reportconfiguration"]
    context_object_name = "config"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        return super().get_context_data(title=self.object.title, **kwargs)

    def get_object(self, queryset: "QuerySet[_M]|None" = None) -> "_M":
        return ReportConfiguration.objects.get(country_office=self.selected_office, id=self.kwargs["pk"])


class OfficeReportDocumentListView(SelectedOfficeMixin, PermissionRequiredMixin, ListView[ReportDocument]):
    template_name = "web/office/document_list.html"
    permission_required = ["power_query.view_reportdocument"]

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        return super().get_context_data(title=_("Available Reports"), **kwargs)

    def get_queryset(self) -> "_SupportsPagination[_M]":
        qs = ReportDocument.objects.filter(report__country_office=self.selected_office)
        if tag := self.request.GET.get("tag", None):
            qs = qs.filter(report__tags__name=tag)
        if active := self.request.GET.get("active", None):
            qs = qs.filter(report__active=parse_bool(active))
        if report := self.request.GET.get("report", None):
            qs = qs.filter(report__name=report)
        return qs.distinct("report", "dataset")


class OfficeReportDocumentDetailView(SelectedOfficeMixin, PermissionRequiredMixin, DetailView[ReportDocument]):
    template_name = "web/office/document.html"
    permission_required = ["power_query.view_reportdocument"]
    context_object_name = "doc"

    def has_permission(self) -> bool:
        obj: "ReportDocument" = self.get_object()
        try:
            perms = self.get_permission_required()
            return self.request.user.has_perms(perms, obj)
        except (PermissionDenied, RequestablePermissionDenied):
            raise RequestablePermissionDenied(obj.report)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        return super().get_context_data(title=self.object.title, **kwargs)

    def get_object(self, queryset: "QuerySet[_M]|None" = None) -> "_M":
        return get_object_or_404(
            ReportDocument.objects.select_related("report"),
            report__country_office=self.selected_office,
            id=self.kwargs["pk"],
        )


class OfficeDocumentDisplayView(SelectedOfficeMixin, PermissionRequiredMixin, DetailView[ReportDocument]):
    permission_required = ["power_query.view_reportconfiguration"]

    def get_object(self, queryset: "QuerySet[_M] | None" = None) -> "_M":
        return ReportDocument.objects.get(report__country_office=self.selected_office, id=self.kwargs["pk"])

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> "RedirectOrResponse":  # type: ignore[override]
        try:
            doc: ReportDocument = self.get_object()
            if not doc.file.size:
                raise FileNotFoundError
            return StreamingHttpResponse(doc.file, content_type=doc.content_type)
        except FileNotFoundError:
            messages.error(request, _("File not found."))
            return HttpResponseRedirectToReferrer(request)


class OfficeDocumentDownloadView(SelectedOfficeMixin, PermissionRequiredMixin, DetailView[ReportDocument]):
    permission_required = ["power_query.download_reportdocument"]

    def get_object(self, queryset: "QuerySet[_M] | None" = None) -> "_M":
        return ReportDocument.objects.get(report__country_office=self.selected_office, id=self.kwargs["pk"])

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> "RedirectOrResponse":  # type: ignore[override]
        try:
            doc: ReportDocument = self.get_object()
            if not doc.file.size:
                raise FileNotFoundError
            response = StreamingHttpResponse(doc.file, content_type="application/force-download")
            response["Content-Disposition"] = f"attachment; filename= {doc.title}{doc.file_suffix}"
            return response
        except FileNotFoundError:
            messages.error(request, _("File not found."))
            return HttpResponseRedirectToReferrer(request)


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


class UserProfileView(SelectedOfficeMixin, UpdateView[User, Any]):
    request: "AuthHttpRequest"
    form_class = UserProfileForm
    model = User
    template_name = "web/office/profile.html"
    success_url = "."

    @cached_property
    def selected_office(self) -> CountryOffice:
        signer = get_cookie_signer()
        return CountryOffice.objects.get(slug=signer.unsign(str(self.request.COOKIES.get(conf.COOKIE_NAME))))

    def get_object(self, queryset: "QuerySet[AbstractBaseUser] | None" = None) -> "User":
        return self.request.user

    def form_valid(self, form: "_ModelFormT") -> "HttpResponse":
        response = super().form_valid(form)
        response.set_cookie(settings.LANGUAGE_COOKIE_NAME, self.request.user.language)
        messages.success(self.request, _("Saved."))
        return response


class RequestAccessView(SelectedOfficeMixin, FormView[Any]):
    form_class = RequestAccessForm
    template_name = "web/office/request_access.html"
    request: "AuthHttpRequest"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        return super().get_context_data(object=self.get_object(), **kwargs)

    def get_success_url(self) -> str:
        return reverse("office-doc-list", args=[self.selected_office.slug])

    def get_object(self, queryset: "QuerySet[AbstractBaseUser] | None" = None) -> "ReportConfiguration":
        return ReportConfiguration.objects.get(country_office=self.selected_office, pk=self.kwargs["id"])

    def form_valid(self, form: "_ModelFormT") -> "HttpResponse":
        res = send_request_access(self.request.user, self.get_object(), message=form.cleaned_data["message"])
        if res == 1:
            messages.success(self.request, _("Request sent."))
        return super().form_valid(form)


@login_required
def download(request: "HttpRequest", path: str) -> "HttpResponse | StreamingHttpResponse":
    return download_media(path)


@login_required
def select_tenant(request: "HttpRequest") -> "HttpResponse":
    if request.method == "POST":
        form = SelectTenantForm(request.POST, request=request)
        if form.is_valid():
            office = form.cleaned_data["tenant"]
            set_selected_tenant(form.cleaned_data["tenant"])
            return HttpResponseRedirect(reverse("office-index", args=[office.slug]))
    else:
        return render(request, "select_tenant.html", {"tenant_form": SelectTenantForm(request=request)})
