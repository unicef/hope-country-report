from django.db import models

from hope_country_report.apps.core.models import CountryOffice
from hope_country_report.apps.power_query.models import Query


class Event(models.Model):
    name = models.CharField(max_length=255, unique=True)
    enabled = models.BooleanField(default=True, blank=True)
    office = models.ForeignKey(CountryOffice, on_delete=models.CASCADE, null=True, blank=True)
    query = models.OneToOneField(Query, on_delete=models.CASCADE, null=True)
    extras = models.JSONField(default=dict, blank=True)
