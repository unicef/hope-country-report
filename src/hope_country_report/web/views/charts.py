from typing import Any, Callable

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponseBase
from django.views.generic import DetailView, ListView

from hope_country_report.apps.power_query.utils import to_dataset

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
    template_name = "web/office/chart.html"
    permission_required = ["power_query.view_chartpage"]
    model = ChartPage

    @classmethod
    def as_view(cls: Any, **initkwargs: Any) -> Callable[..., HttpResponseBase]:
        return super().as_view(**initkwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        chart_page = self.object
        context["title"] = chart_page.title
        if chart_page.query:
            all_data = []
            for dataset in chart_page.query.datasets.all():
                all_data.extend(dataset.data)  # Assuming 'data' is a list-like structure

            context["json_data"] = to_dataset(all_data).export("json")
        else:
            context["json_data"] = None
        return context
