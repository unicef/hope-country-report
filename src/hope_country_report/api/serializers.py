from rest_framework import serializers
from rest_framework_nested.relations import NestedHyperlinkedRelatedField
from rest_framework_nested.serializers import NestedHyperlinkedModelSerializer

from hope_country_report.apps.core.models import CountryOffice
from hope_country_report.apps.power_query.models import Query


class QueryDataSerializer(serializers.HyperlinkedModelSerializer):
    # parent_lookup_kwargs = {
    #     "country_office": "country_office__slug",
    # }
    country_office = NestedHyperlinkedRelatedField(
        view_name="countryoffice-detail", lookup_field="slug", read_only=True
    )

    class Meta:
        model = Query
        fields = ["name", "description", "country_office"]


class CountryOfficeSerializer(NestedHyperlinkedModelSerializer):
    # id = serializers.HyperlinkedIdentityField(view_name="office-detail", read_only=True)

    queries = NestedHyperlinkedRelatedField(
        view_name="office-queries-list",
        read_only=True,
        parent_lookup_kwargs={"slug": "office__slug"},
        lookup_url_kwarg="slug",
    )

    class Meta:
        model = CountryOffice
        fields = ("id", "name", "active", "slug", "hope_id", "queries", "url")
        lookup_field = "slug"
        extra_kwargs = {"url": {"lookup_field": "slug"}}

    # queries = HyperlinkedIdentityField(
    #     view_name='office-query-list',
    #     lookup_url_kwarg='office'
    # )
