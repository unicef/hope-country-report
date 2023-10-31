from typing import Any, TYPE_CHECKING, TypeVar

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.signing import get_cookie_signer
from django.db.models import Model
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, StreamingHttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils.functional import cached_property
from django.views import View
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, ListView, TemplateView, UpdateView

import django_stubs_ext
from adminfilters.utils import parse_bool

from hope_country_report.apps.core.models import CountryOffice, User
from hope_country_report.apps.power_query.models import ReportDocument
from hope_country_report.apps.tenant.config import conf
from hope_country_report.apps.tenant.forms import SelectTenantForm
from hope_country_report.apps.tenant.utils import set_selected_tenant
from hope_country_report.utils.media import download_media
from hope_country_report.web.forms import UserProfileForm

django_stubs_ext.monkeypatch()

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractBaseUser
    from django.core.paginator import _SupportsPagination
    from django.db.models import QuerySet
    from django.views.generic.edit import _ModelFormT

    _M = TypeVar("_M", bound=Model, covariant=True)


@login_required
def index(request: "HttpRequest") -> "HttpResponse":
    return render(request, "home.html", {"tenant_form": SelectTenantForm(request=request)})


class SelectedOfficeMixin(LoginRequiredMixin, View):
    @cached_property
    def selected_office(self) -> CountryOffice:
        return CountryOffice.objects.get(slug=self.kwargs["co"])

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


class OfficeReportListView(SelectedOfficeMixin, PermissionRequiredMixin, ListView[ReportDocument]):
    template_name = "web/office/reports.html"
    permission_required = ["power_query.view_report"]
    # context_object_name = "doc"

    def get_queryset(self) -> "_SupportsPagination[_M]":
        qs = ReportDocument.objects.filter(report__country_office=self.selected_office)
        if tag := self.request.GET.get("tag", None):
            qs = qs.filter(report__tags__name=tag)
        if active := self.request.GET.get("active", None):
            qs = qs.filter(report__active=parse_bool(active))
        return qs.distinct("report", "dataset")


class OfficeReportDetailView(SelectedOfficeMixin, DetailView[ReportDocument]):
    template_name = "web/office/report.html"
    context_object_name = "doc"

    def get_object(self, queryset: "QuerySet[_M]|None" = None) -> "_M":
        return ReportDocument.objects.select_related("report").get(
            report__country_office=self.selected_office, id=self.kwargs["pk"]
        )


class OfficeDocumentDisplayView(SelectedOfficeMixin, View):
    def get_object(self, queryset: "QuerySet[_M] | None" = None) -> "_M":
        return ReportDocument.objects.get(
            report__country_office=self.selected_office, report=self.kwargs["report"], id=self.kwargs["pk"]
        )

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> StreamingHttpResponse:
        doc: ReportDocument = self.get_object()
        return StreamingHttpResponse(doc.file, content_type=doc.content_type)


class OfficeDocumentDownloadView(SelectedOfficeMixin, View):
    def get_object(self) -> "_M":
        return ReportDocument.objects.get(
            report__country_office=self.selected_office, report=self.kwargs["report"], id=self.kwargs["pk"]
        )

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> StreamingHttpResponse:
        doc: ReportDocument = self.get_object()
        response = StreamingHttpResponse(doc.file, content_type="application/force-download")
        response["Content-Disposition"] = f"attachment; filename= {doc.title}{doc.file_suffix}"
        return response


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


class UserProfileView(SelectedOfficeMixin, UpdateView["User, _ModelFormT"]):
    form_class = UserProfileForm
    model = User
    template_name = "web/office/profile.html"
    success_url = "."

    @property
    def selected_office(self) -> CountryOffice:
        signer = get_cookie_signer()
        return CountryOffice.objects.get(slug=signer.unsign(str(self.request.COOKIES.get(conf.COOKIE_NAME))))

    def get_object(self, queryset: "QuerySet[AbstractBaseUser] | None" = None) -> "User":
        return self.request.user  # type: ignore[return-value]

    def form_valid(self, form: "_ModelFormT") -> "HttpResponse":
        response = super().form_valid(form)
        response.set_cookie(settings.LANGUAGE_COOKIE_NAME, self.request.user.language)
        return response


@login_required
def download(request: "HttpRequest", path: str) -> "HttpResponse | StreamingHttpResponse":
    return download_media(path)


@require_POST
@login_required
def select_tenant(request: "HttpRequest") -> "HttpResponse":
    if request.method == "POST":
        form = SelectTenantForm(request.POST, request=request)
        if form.is_valid():
            office = form.cleaned_data["tenant"]
            set_selected_tenant(form.cleaned_data["tenant"])
            return HttpResponseRedirect(reverse("office-index", args=[office.slug]))
