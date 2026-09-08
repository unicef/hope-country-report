import json
from typing import TYPE_CHECKING, Any

from django.core.serializers import serialize
from django.http import JsonResponse, StreamingHttpResponse
from django_filters import rest_framework as filters
from rest_framework import permissions, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_extensions.mixins import NestedViewSetMixin

from ..apps.core.models import CountryOffice, CountryShape
from ..apps.power_query.exceptions import RequestablePermissionDenied
from ..apps.power_query.models import ChartPage, Dataset, Query, ReportConfiguration, ReportDocument
from ..apps.tenant.config import conf
from .serializers import (
    BoundarySerializer,
    ChartPageSerializer,
    CountryOfficeSerializer,
    DatasetListSerializer,
    DatasetDetailSerializer,
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


class TenantScopedViewSetMixin:
    """Scope querysets to the CountryOffices the requesting user may access.

    Scoping relies on ``request.user`` (via ``get_allowed_tenants``) rather than the
    thread-local tenant so that it also holds for token-authenticated requests, where
    the state middleware cannot resolve a tenant.
    """

    request: Any

    def allowed_office_ids(self) -> "Any":
        return conf.auth.get_allowed_tenants(self.request).values("pk")

    def apply_parent_lookups(self, queryset: "Any") -> "Any":
        if hasattr(self, "filter_queryset_by_parents_lookups"):
            return self.filter_queryset_by_parents_lookups(queryset)
        return queryset


class HCRHomeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CountryOffice.objects.all().order_by("slug")
    serializer_class = LocationSerializer
    permission_classes = [permissions.DjangoObjectPermissions]

    def list(self, request: "AnyRequest", *args: tuple[Any], **kwargs: dict[str, str]) -> Response:
        return Response({})

    @action(detail=False)
    def topology(self, request: "AnyRequest") -> JsonResponse:
        from pytopojson import topology

        topology_ = topology.Topology()

        qs = CountryShape.objects.all()
        geojson = json.loads(serialize("geojson", qs, geometry_field="mpoly", id_field="un", fields=["name", "active"]))

        topojson = topology_({"countries": geojson}, quantization=0)

        return JsonResponse(topojson, content_type="application/json", safe=False)

    @action(detail=False)
    def boundaries(self, request: "AnyRequest") -> JsonResponse:
        qs = CountryShape.objects.all()
        ser = BoundarySerializer(qs, many=True)
        return JsonResponse(ser.data, content_type="application/json")

    @action(detail=False)
    def offices(self, request: "AnyRequest") -> JsonResponse:
        qs = (
            conf.auth.get_allowed_tenants(request)
            .filter(active=True)
            .values_list("shape__iso3", "name", "active")
        )
        return JsonResponse(list(qs), safe=False, content_type="application/json")


class CountryOfficeFilter(filters.FilterSet):
    slug = filters.CharFilter(lookup_expr="istartswith")


class CountryOfficeViewSet(TenantScopedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    queryset = CountryOffice.objects.all()
    serializer_class = CountryOfficeSerializer
    permission_classes = [permissions.DjangoObjectPermissions]
    filterset_class = CountryOfficeFilter
    lookup_field = "slug"

    def get_queryset(self):
        return conf.auth.get_allowed_tenants(self.request)


class QueryViewSet(TenantScopedViewSetMixin, NestedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Query.objects.all()
    serializer_class = QuerySerializer
    permission_classes = [permissions.DjangoObjectPermissions]

    def get_queryset(self):
        queryset = Query.objects.filter(country_office__in=self.allowed_office_ids())
        return self.apply_parent_lookups(queryset).order_by("-pk")

    @action(detail=True, methods=["get"])
    def latest_dataset(self, request, *args, **kwargs):
        """
        Get the latest dataset for this query, including its data.
        """
        query = self.get_object()
        latest_dataset = query.datasets.order_by("-last_run", "-pk").first()

        if not latest_dataset:
            return Response({"detail": "No datasets found for this query."}, status=status.HTTP_404_NOT_FOUND)

        if not request.user.has_perm("power_query.view_dataset", latest_dataset):
            return Response(
                {"detail": "You do not have permission to access this dataset."}, status=status.HTTP_403_FORBIDDEN
            )

        serializer = DatasetDetailSerializer(latest_dataset, context={"request": request})
        return Response(serializer.data)


class ChartViewSet(TenantScopedViewSetMixin, NestedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    queryset = ChartPage.objects.all()
    serializer_class = ChartPageSerializer
    permission_classes = [permissions.DjangoObjectPermissions]

    def get_queryset(self):
        queryset = ChartPage.objects.filter(country_office__in=self.allowed_office_ids())
        return self.apply_parent_lookups(queryset).order_by("-pk")


class DatasetViewSet(TenantScopedViewSetMixin, NestedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = DatasetListSerializer
    permission_classes = [permissions.DjangoObjectPermissions]

    def get_queryset(self):
        queryset = Dataset.objects.filter(query__country_office__in=self.allowed_office_ids())
        queryset = self.apply_parent_lookups(queryset)
        query_id = self.kwargs.get("parent_lookup_query")
        if query_id:
            queryset = queryset.filter(query_id=query_id)

        reserved = {"page", "page_size", "format"}
        filters = {}
        for key, value in self.request.query_params.items():
            if key not in reserved:
                filters[f"info__arguments__{key}"] = value

        if filters:
            queryset = queryset.filter(**filters)

        return queryset

    def get_serializer_class(self):
        if self.action == "list":

            class _DatasetListSerializer(DatasetListSerializer):
                data = serializers.IntegerField(source="size")

                class Meta(DatasetListSerializer.Meta):
                    fields = DatasetListSerializer.Meta.fields + ["data"]

            return _DatasetListSerializer

        if self.action == "retrieve":
            return DatasetDetailSerializer
        return super().get_serializer_class()

    @action(detail=True)
    def data(self, request, *args, **kwargs):
        from rest_framework.pagination import PageNumberPagination

        dataset = self.get_object()
        data = dataset.data
        if hasattr(data, "dict"):
            data = data.dict

        if isinstance(data, list):
            paginator = PageNumberPagination()
            paginator.page_size_query_param = "page_size"

            page = paginator.paginate_queryset(data, request, view=self)
            if page is not None:
                return paginator.get_paginated_response(page)

        return Response(data)


class ReportViewSet(TenantScopedViewSetMixin, NestedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = ReportConfigurationSerializer
    permission_classes = [permissions.DjangoObjectPermissions]
    filterset_fields = ["name"]

    def get_queryset(self):
        queryset = ReportConfiguration.objects.filter(country_office__in=self.allowed_office_ids())
        return self.apply_parent_lookups(queryset).order_by("-pk")


class DocumentViewSet(
    TenantScopedViewSetMixin,
    NestedViewSetMixin,
    SelectedOfficeViewSet,
    viewsets.ReadOnlyModelViewSet,
):
    serializer_class = ReportDocumentSerializer
    permission_classes = [permissions.DjangoObjectPermissions]

    def get_queryset(self):
        queryset = ReportDocument.objects.filter(report__visible=True)
        queryset = queryset.filter(report__country_office__in=self.allowed_office_ids())
        return self.apply_parent_lookups(queryset).order_by("-pk")

    @action(detail=True)
    def download(
        self,
        request: "AnyRequest",
        *args: tuple[Any],
        **kwargs: dict[str, str],
    ) -> "Response|StreamingHttpResponse":
        try:
            doc: ReportDocument = self.get_object()
            if not request.user.has_perm("power_query.download_reportdocument", doc):
                return Response(
                    {"detail": "You do not have permission to download this document."},
                    status=status.HTTP_403_FORBIDDEN,
                )
        except RequestablePermissionDenied:
            return Response(
                {"detail": "This document is restricted. Please request access first."},
                status=status.HTTP_403_FORBIDDEN,
            )
        try:
            if not doc.file.size:
                raise FileNotFoundError
            response = StreamingHttpResponse(doc.file, content_type="application/force-download")
            response["Content-Disposition"] = f"attachment; filename= {doc.filename}"
            return response
        except FileNotFoundError:
            return Response({"Error": 404}, status=404)
