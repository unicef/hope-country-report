from typing import Any, TYPE_CHECKING, TypeVar

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.utils.translation import gettext_lazy as _
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

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        return super().get_context_data(title=_("Configured Reports"), **kwargs)

    def get_queryset(self) -> "_SupportsPagination[_M]":
        qs = ReportConfiguration.objects.filter(country_office=self.selected_office, visible=True)
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
