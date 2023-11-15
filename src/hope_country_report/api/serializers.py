from djgeojson.fields import MultiPolygonField
from rest_framework import serializers
from rest_framework_gis.fields import GeometrySerializerMethodField
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from hope_country_report.apps.core.models import CountryOffice, CountryShape
from hope_country_report.apps.power_query.models import Dataset, Query, ReportConfiguration, ReportDocument


class QuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Query
        fields = ["id", "name", "description", "country_office"]


class DatasetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dataset
        fields = ["hash", "last_run"]


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
    url = serializers.HyperlinkedIdentityField(view_name="api:countryoffice-detail", lookup_field="slug")

    class Meta:
        model = CountryOffice
        fields = ("id", "name", "active", "slug", "hope_id", "url")
        lookup_field = "slug"


class ReportConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportConfiguration
        fields = ["id", "country_office", "title", "query", "formatters"]


class ReportDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportDocument
        fields = ["id", "title", "report", "dataset", "formatter", "filename"]
