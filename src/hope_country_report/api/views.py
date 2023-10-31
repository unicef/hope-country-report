from rest_framework import permissions, viewsets

from ..apps.power_query.models import Query
from .serializers import QueryDataSerializer


class QueryDataViewSet(viewsets.ModelViewSet):
    queryset = Query.objects.all().order_by("-pk")
    serializer_class = QueryDataSerializer
    permission_classes = [permissions.IsAuthenticated]
