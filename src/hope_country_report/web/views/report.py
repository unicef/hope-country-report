from typing import Any, TYPE_CHECKING, TypeVar

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Count
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import DetailView, ListView

from adminfilters.utils import parse_bool

from hope_country_report.apps.power_query.models import ReportConfiguration

from .base import SelectedOfficeMixin

if TYPE_CHECKING:
    from django.core.paginator import _SupportsPagination
    from django.db.models import Model, QuerySet

    _M = TypeVar("_M", bound=Model, covariant=True)


class OfficeConfigurationListView(SelectedOfficeMixin, PermissionRequiredMixin, ListView[ReportConfiguration]):
    template_name = "web/office/config_list.html"
    permission_required = ["power_query.view_reportconfiguration"]
    paginate_by = 50
    ordering_fields = [
        "title",
        "active",
        "last_run",
        "schedule",
        "compress",
        "protect",
        "parametrized",
        "restricted",
    ]

    def get_ordering(self):
        ordering = self.request.GET.get("ordering", "title")
        # prevent ordering by arbitrary fields
        if ordering.lstrip("-") not in self.ordering_fields:
            return "title"
        return ordering

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(title=_("Configured Reports"), **kwargs)
        current_ordering = self.get_ordering()
        context["ordering"] = current_ordering

        # Build URLs for sorting headers
        sort_urls = {}
        params = self.request.GET.copy()
        for field in self.ordering_fields:
            p = params.copy()
            if field == current_ordering.lstrip("-"):
                # Toggle direction
                if current_ordering.startswith("-"):
                    p["ordering"] = field
                else:
                    p["ordering"] = f"-{field}"
            else:
                p["ordering"] = field
            sort_urls[field] = p.urlencode()
        context["sort_urls"] = sort_urls

        # For pagination
        page_params = self.request.GET.copy()
        if "page" in page_params:
            del page_params["page"]
        context["page_params"] = page_params.urlencode()

        if report_name := self.request.GET.get("report"):
            try:
                report = ReportConfiguration.objects.only("title").get(
                    country_office=self.selected_office, name=report_name
                )
                context["report_filter_title"] = report.title
            except ReportConfiguration.DoesNotExist:
                context["report_filter_title"] = report_name

        return context

    def get_queryset(self) -> "_SupportsPagination[_M]":
        qs = ReportConfiguration.objects.filter(country_office=self.selected_office, visible=True)
        if tag := self.request.GET.get("tag", None):
            qs = qs.filter(tags__name=tag)
        if active := self.request.GET.get("active", None):
            qs = qs.filter(active=parse_bool(active))
        if report_name := self.request.GET.get("report", None):
            qs = qs.filter(name=report_name)

        qs = qs.annotate(
            restricted_count=Count("limit_access_to", distinct=True),
            is_parametrized=Count("query__parametrizer", distinct=True),
        )

        ordering = self.get_ordering()

        if "parametrized" in ordering:
            ordering = ordering.replace("parametrized", "is_parametrized")
        if "restricted" in ordering:
            ordering = ordering.replace("restricted", "restricted_count")

        return qs.order_by(ordering)


class OfficeConfigurationDetailView(SelectedOfficeMixin, PermissionRequiredMixin, DetailView[ReportConfiguration]):
    template_name = "web/office/config.html"
    permission_required = ["power_query.view_reportconfiguration"]
    context_object_name = "config"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        return super().get_context_data(title=self.object.title, **kwargs)

    def get_object(self, queryset: "QuerySet[_M]|None" = None) -> "_M":
        return ReportConfiguration.objects.get(country_office=self.selected_office, id=self.kwargs["pk"])


class OfficeConfigurationRunView(SelectedOfficeMixin, PermissionRequiredMixin, View):
    permission_required = "power_query.change_reportconfiguration"
    http_method_names = ["post"]

    def get_report(self) -> "ReportConfiguration":
        return ReportConfiguration.objects.get(country_office=self.selected_office, id=self.kwargs["pk"])

    def post(self, request: Any, *args: Any, **kwargs: Any) -> JsonResponse:
        report = self.get_report()
        if report.is_running:
            return JsonResponse(
                {"status": "error", "message": _("Report is already running.")},
                status=409,  # Conflict
            )
        report.queue()
        return JsonResponse({"status": "ok", "message": _("Report task queued.")})
