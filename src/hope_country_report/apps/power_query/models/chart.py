from django.db import models
from django.urls import reverse

from hope_country_report.apps.core.models import CountryOffice

from .query import Query


class ChartPage(models.Model):
    country_office = models.ForeignKey(CountryOffice, on_delete=models.CASCADE)
    title = models.CharField(max_length=100, db_index=True)
    template = models.CharField(max_length=250, default=None, blank=True, null=True)

    query = models.ForeignKey(Query, blank=True, null=True, on_delete=models.SET_NULL)
    datasource = models.CharField(max_length=500, null=True, blank=True)

    params = models.JSONField(default=dict, null=False, blank=True)

    class Meta:
        ordering = ("title",)

    class Tenant:
        tenant_filter_field = "country_office"

    def get_absolute_url(self):
        return reverse("office-chart", args=[self.country_office.slug, self.pk])
