from djgeojson.fields import MultiPolygonField
from rest_framework import serializers
from rest_framework_gis.fields import GeometrySerializerMethodField
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from rest_framework_nested.relations import NestedHyperlinkedRelatedField

from hope_country_report.apps.core.models import CountryOffice, CountryShape
from hope_country_report.apps.power_query.models import Query


class QueryDataSerializer(serializers.HyperlinkedModelSerializer):
    country_office = NestedHyperlinkedRelatedField(
        view_name="countryoffice-detail", lookup_field="slug", read_only=True
    )

    class Meta:
        model = Query
        fields = ["name", "description", "country_office"]


class LocationSerializer(GeoFeatureModelSerializer):
    geom = GeometrySerializerMethodField()

    class Meta:
        model = CountryOffice
        geo_field = "geom"
        fields = ("id", "name", "geom")

    def get_geom(self, obj: "CountryOffice") -> "MultiPolygonField|None":
        try:
            return obj.shape.mpoly
        except CountryShape.DoesNotExist:
            return None


class BoundarySerializer(GeoFeatureModelSerializer):
    class Meta:
        model = CountryShape
        geo_field = "mpoly"
        fields = ("name", "mpoly", "iso2", "iso3", "un")


class CountryOfficeSerializer(serializers.HyperlinkedModelSerializer):
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
