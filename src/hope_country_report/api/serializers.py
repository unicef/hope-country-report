from typing import TYPE_CHECKING, Any

from django.utils.functional import cached_property
from rest_framework import serializers
from rest_framework.reverse import reverse
from rest_framework_gis.fields import GeometrySerializerMethodField
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from hope_country_report.apps.core.models import CountryOffice, CountryShape
from hope_country_report.apps.power_query.models import ChartPage, Dataset, Query, ReportConfiguration, ReportDocument
from hope_country_report.apps.power_query.utils import to_dataset

if TYPE_CHECKING:
    from django.db.models import Model
    from djgeojson.fields import MultiPolygonField


class SelectedOfficeSerializer(serializers.ModelSerializer):
    co_key = "parent_lookup_country_office__slug"
    office = serializers.SerializerMethodField()

    class Meta:
        model = ReportConfiguration
        fields = [
            "office",
        ]

    @cached_property
    def selected_office(self) -> CountryOffice:
        co_slug: str = self.context["view"].kwargs.get(self.co_key)
        if not co_slug:
            raise serializers.ValidationError("Country office slug is required.")
        return CountryOffice.objects.get(slug=co_slug)

    def get_office(self, obj: "Model"):
        return self.context["request"].build_absolute_uri(
            reverse("api:countryoffice-detail", args=[self.selected_office.slug])
        )


class CountryOfficeSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="api:countryoffice-detail", lookup_field="slug")
    queries = serializers.HyperlinkedIdentityField(
        view_name="api:queries-list", lookup_field="slug", lookup_url_kwarg="parent_lookup_country_office__slug"
    )
    configs = serializers.HyperlinkedIdentityField(
        view_name="api:config-list", lookup_field="slug", lookup_url_kwarg="parent_lookup_country_office__slug"
    )

    class Meta:
        model = CountryOffice
        fields = ("id", "name", "active", "slug", "hope_id", "url", "queries", "configs")
        lookup_field = "slug"


class QuerySerializer(SelectedOfficeSerializer):
    class Meta:
        model = Query
        fields = ["id", "name", "description", "office"]


class DatasetSerializer(serializers.ModelSerializer):
    data = serializers.SerializerMethodField()

    class Meta:
        model = Dataset
        fields: list[str] = ["hash", "last_run", "data"]

    def get_data(self, obj: Dataset) -> str:
        return to_dataset(obj.data).export("json")


class ReportConfigurationSerializer(SelectedOfficeSerializer):
    url = serializers.SerializerMethodField()
    documents = serializers.SerializerMethodField()

    class Meta:
        model = ReportConfiguration
        fields = ["id", "office", "name", "title", "query", "formatters", "url", "documents"]

    def get_url(self, obj: ReportConfiguration) -> str:
        return self.context["request"].build_absolute_uri(
            reverse("api:config-detail", args=[self.selected_office.slug, obj.pk])
        )

    def get_documents(self, obj: ReportConfiguration) -> str:
        return self.context["request"].build_absolute_uri(
            reverse("api:document-list", args=[self.selected_office.slug, obj.pk])
        )


class ReportDocumentSerializer(SelectedOfficeSerializer):
    url = serializers.SerializerMethodField()
    site_url = serializers.SerializerMethodField()
    co_key = "parent_lookup_report__country_office__slug"

    class Meta:
        model = ReportDocument
        fields = [
            "id",
            "url",
            "title",
            "report",
            "dataset",
            "formatter",
            "filename",
            "office",
            "file_suffix",
            "compressed",
            "protected",
            "content_type",
            "site_url",
        ]

    def get_url(self, obj: ReportDocument) -> str:
        return self.context["request"].build_absolute_uri(
            reverse("api:document-detail", args=[self.selected_office.slug, obj.report.pk, obj.pk])
        )

    def get_site_url(self, obj: ReportDocument) -> str:
        return self.context["request"].build_absolute_uri(obj.get_absolute_url())


class LocationSerializer(GeoFeatureModelSerializer):
    geom = GeometrySerializerMethodField()

    class Meta:
        model = CountryOffice
        geo_field = "geom"
        fields = ("id", "name", "geom")

    def get_geom(self, obj: "CountryOffice") -> "MultiPolygonField[Any]|None":
        try:
            return obj.shape.mpoly
        except CountryShape.DoesNotExist:
            return None


class BoundarySerializer(GeoFeatureModelSerializer):
    class Meta:
        model = CountryShape
        geo_field = "mpoly"
        fields = ("name", "mpoly", "iso2", "iso3", "un")


class ChartPageSerializer(serializers.ModelSerializer):
    detail_url = serializers.SerializerMethodField()

    class Meta:
        model = ChartPage
        fields = ["id", "country_office", "title", "params", "detail_url"]

    def get_detail_url(self, obj: ChartPage) -> str:
        return self.context["request"].build_absolute_uri(
            reverse("office-chart", args=[obj.country_office.slug, obj.pk])
        )
