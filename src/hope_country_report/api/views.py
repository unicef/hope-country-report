from django.db.models import QuerySet

from rest_framework import permissions, viewsets

from ..apps.core.models import CountryOffice
from ..apps.power_query.models import Query
from .serializers import CountryOfficeSerializer, QueryDataSerializer


class SelectedOfficeViewSet(viewsets.ReadOnlyModelViewSet):
    def selected_office(self) -> CountryOffice:
        return CountryOffice.objects.get(id=self.kwargs["slug"])


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
