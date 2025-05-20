from typing import Any, TYPE_CHECKING, TypeVar

from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, StreamingHttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, ListView
from django.views.generic.edit import FormView

from admin_extra_buttons.utils import HttpResponseRedirectToReferrer
from adminfilters.utils import parse_bool

from hope_country_report.apps.power_query.exceptions import RequestablePermissionDenied
from hope_country_report.apps.power_query.models import ReportConfiguration, ReportDocument
from hope_country_report.utils.mail import send_request_access
from hope_country_report.web.forms import RequestAccessForm

from .base import SelectedOfficeMixin

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractBaseUser
    from django.core.paginator import _SupportsPagination
    from django.db.models import Model, QuerySet
    from django.views.generic.edit import _ModelFormT

    from hope_country_report.types.http import AuthHttpRequest, RedirectOrResponse

    _M = TypeVar("_M", bound=Model, covariant=True)


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

    def handle_no_permission(self) -> HttpResponseRedirect:
        if not self.has_permission():
            raise RequestablePermissionDenied(self.get_object().report)
        return super().handle_no_permission()

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
            report__visible=True,
            id=self.kwargs["pk"],
        )


class OfficeDocumentDisplayView(SelectedOfficeMixin, PermissionRequiredMixin, DetailView[ReportDocument]):
    permission_required = ["power_query.view_reportconfiguration"]

    def get_object(self, queryset: "QuerySet[_M] | None" = None) -> "_M":
        return ReportDocument.objects.get(
            report__country_office=self.selected_office, id=self.kwargs["pk"], report__visible=True
        )

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
