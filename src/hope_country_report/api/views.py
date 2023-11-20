from typing import Any, Dict, Tuple, TYPE_CHECKING

import json

from django.core.serializers import serialize
from django.http import JsonResponse, StreamingHttpResponse

from django_filters import rest_framework as filters
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_extensions.mixins import NestedViewSetMixin

from ..apps.core.models import CountryOffice, CountryShape
from ..apps.power_query.models import Dataset, Query, ReportConfiguration, ReportDocument
from .serializers import (
    BoundarySerializer,
    CountryOfficeSerializer,
    DatasetSerializer,
    LocationSerializer,
    QuerySerializer,
    ReportConfigurationSerializer,
    ReportDocumentSerializer,
)

if TYPE_CHECKING:
    from ..types.http import AnyRequest


class SelectedOfficeViewSet(viewsets.ReadOnlyModelViewSet):
    def selected_office(self) -> CountryOffice:
        return CountryOffice.objects.get(id=self.kwargs["slug"])


class HCRHomeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CountryOffice.objects.all().order_by("slug")
    serializer_class = LocationSerializer
    permission_classes = [permissions.DjangoObjectPermissions]

    def list(self, request: "AnyRequest", *args: Tuple[Any], **kwargs: Dict[str, str]) -> Response:
        return Response({})

    @action(detail=False)
    # @method_decorator(cache_page(60*60*2))
    def topology(self, request: "AnyRequest") -> JsonResponse:
        from pytopojson import topology

        topology_ = topology.Topology()

        qs = CountryShape.objects.filter()
        geojson = json.loads(serialize("geojson", qs, geometry_field="mpoly", id_field="un", fields=["name"]))

        topojson = topology_({"countries": geojson}, quantization=0)

        return JsonResponse(topojson, content_type="application/json", safe=False)

    # @action(detail=False)
    # # @method_decorator(cache_page(60*60*2))
    # def topology_file(self, request):
    #     fname = resource_path("apps/charts/datasets/topology.json")
    #     data = json.load(fname.open("r"))
    #     return JsonResponse(data, content_type="application/json")

    @action(detail=False)
    # @method_decorator(cache_page(60*60*2))
    def boundaries(self, request: "AnyRequest") -> JsonResponse:
        qs = CountryShape.objects.all()
        ser = BoundarySerializer(qs, many=True)
        return JsonResponse(ser.data, content_type="application/json")

    @action(detail=False)
    def offices(self, request: "AnyRequest") -> JsonResponse:
        qs = CountryOffice.objects.filter(active=True).values_list("shape__iso3", "name")
        return JsonResponse(list(qs), safe=False, content_type="application/json")

    # @action(detail=False)
    # def country_names(self, request):
    #     fname = resource_path("apps/charts/data/world-country-names.tsv")
    #     data = fname.read_bytes()
    #     # qs = CountryOffice.objects.filter(shape__isnull=True).select_related("shape").order_by("slug")
    #     # ser = LocationSerializer(qs, many=True)
    #     return HttpResponse(data, content_type="text/plain")


class CountryOfficeFilter(filters.FilterSet):
    slug = filters.CharFilter(lookup_expr="istartswith")


class CountryOfficeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CountryOffice.objects.all()
    serializer_class = CountryOfficeSerializer
    permission_classes = [permissions.DjangoObjectPermissions]
    filterset_class = CountryOfficeFilter
    lookup_field = "slug"

    # @action(detail=True)
    # def queries(self, **kwargs):
    #     return HttpResponseRedirect(reverse("api:queries-list", args=[kwargs["slug"]]))


class QueryViewSet(NestedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Query.objects.all().order_by("-pk")
    serializer_class = QuerySerializer
    permission_classes = [permissions.DjangoObjectPermissions]


class DatasetViewSet(NestedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Dataset.objects.all().order_by("-pk")
    serializer_class = DatasetSerializer
    permission_classes = [permissions.DjangoObjectPermissions]


class ReportViewSet(NestedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    queryset = ReportConfiguration.objects.all().order_by("-pk")
    serializer_class = ReportConfigurationSerializer
    permission_classes = [permissions.DjangoObjectPermissions]


class DocumentViewSet(NestedViewSetMixin, SelectedOfficeViewSet, viewsets.ReadOnlyModelViewSet):
    queryset = ReportDocument.objects.all().order_by("-pk")
    serializer_class = ReportDocumentSerializer
    permission_classes = [permissions.DjangoObjectPermissions]

    @action(detail=True)
    def download(
        self,
        request: "AnyRequest",
        parent_lookup_report__country_office__slug: str,
        parent_lookup_report__id: str,
        pk: str,
    ) -> "Response|StreamingHttpResponse":
        try:
            doc = ReportDocument.objects.get(
                report__country_office__slug=parent_lookup_report__country_office__slug,
                report__id=parent_lookup_report__id,
                pk=pk,
            )
            if not doc.file.size:
                raise FileNotFoundError
            response = StreamingHttpResponse(doc.file, content_type="application/force-download")
            response["Content-Disposition"] = f"attachment; filename= {doc.filename}"
            return response
        except FileNotFoundError:
            return Response({"Error": 404}, status=404)
