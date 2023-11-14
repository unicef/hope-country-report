import json

from django.core.serializers import serialize
from django.db.models import QuerySet
from django.http import HttpResponse, JsonResponse

from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ..apps.core.models import CountryOffice, CountryShape
from ..apps.power_query.models import Query
from ..utils.media import resource_path
from .serializers import CountryOfficeSerializer, LocationSerializer, QueryDataSerializer, BoundarySerializer


class SelectedOfficeViewSet(viewsets.ReadOnlyModelViewSet):
    def selected_office(self) -> CountryOffice:
        return CountryOffice.objects.get(id=self.kwargs["slug"])


class HCRHomeView(viewsets.ReadOnlyModelViewSet):
    queryset = CountryOffice.objects.all().order_by("slug")
    serializer_class = LocationSerializer
    permission_classes = [permissions.DjangoObjectPermissions]

    def list(self, request, *args, **kwargs):
        return Response({})

    @action(detail=False)
    # @method_decorator(cache_page(60*60*2))
    def topology(self, request):
        from pytopojson import topology

        topology_ = topology.Topology()

        # fname = resource_path("apps/charts/data/topology.json")
        # data = json.load(fname.open("r"))
        qs = CountryShape.objects.filter()
        # ser = LocationSerializer(qs, many=True)
        geojson = json.loads(serialize("geojson", qs, geometry_field="mpoly", id_field="un", fields=["name"]))

        topojson = topology_({"countries": geojson}, quantization=0)

        return JsonResponse(topojson, content_type="text/json", safe=False)

    @action(detail=False)
    # @method_decorator(cache_page(60*60*2))
    def topology_file(self, request):
        fname = resource_path("apps/charts/datasets/topology.json")
        data = json.load(fname.open("r"))
        return JsonResponse(data, content_type="text/json")

    @action(detail=False)
    # @method_decorator(cache_page(60*60*2))
    def boundaries(self, request):
        qs = CountryShape.objects.all()
        ser = BoundarySerializer(qs, many=True)
        return JsonResponse(ser.data, content_type="text/json")

    @action(detail=False)
    def offices(self, request):
        qs = CountryOffice.objects.filter(active=True).values_list("shape__iso3", "name")
        return JsonResponse(list(qs), safe=False, content_type="text/plain")

    @action(detail=False)
    def country_names(self, request):
        fname = resource_path("apps/charts/data/world-country-names.tsv")
        data = fname.read_bytes()
        # qs = CountryOffice.objects.filter(shape__isnull=True).select_related("shape").order_by("slug")
        # ser = LocationSerializer(qs, many=True)
        return HttpResponse(data, content_type="text/plain")


class CountryOfficeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CountryOffice.objects.all().order_by("slug")
    serializer_class = CountryOfficeSerializer
    permission_classes = [permissions.DjangoObjectPermissions]
    lookup_field = "slug"


class QueryDataViewSet(SelectedOfficeViewSet):
    queryset = Query.objects.all().order_by("-pk")
    serializer_class = QueryDataSerializer
    permission_classes = [permissions.DjangoObjectPermissions]

    def get_queryset(self) -> QuerySet[Query]:
        return Query.objects.filter(country_office__slug=self.kwargs["office_slug"])
