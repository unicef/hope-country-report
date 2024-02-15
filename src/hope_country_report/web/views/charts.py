from typing import Any, Callable

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponseBase
from django.views.generic import DetailView, ListView

from ...apps.power_query.models import ChartPage
from .base import SelectedOfficeMixin


class ChartListView(SelectedOfficeMixin, PermissionRequiredMixin, ListView[ChartPage]):
    template_name = "web/office/chart_list.html"
    permission_required = ["power_query.view_chartpage"]
    model = ChartPage

    @classmethod
    def as_view(cls: Any, **initkwargs: Any) -> Callable[..., HttpResponseBase]:
        return super().as_view(**initkwargs)


class ChartDetailView(SelectedOfficeMixin, PermissionRequiredMixin, DetailView[ChartPage]):
    template_name = "slick_reporting/report.html"
    permission_required = ["power_query.view_chartpage"]
    model = ChartPage

    @classmethod
    def as_view(cls: Any, **initkwargs: Any) -> Callable[..., HttpResponseBase]:
        return super().as_view(**initkwargs)
