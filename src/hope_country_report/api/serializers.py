from rest_framework import serializers

from hope_country_report.apps.power_query.models import Query


class QueryDataSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Query
        fields = ["url", "username", "email", "groups"]
