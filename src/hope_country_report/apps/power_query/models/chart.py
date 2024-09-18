from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse

from hope_country_report.apps.core.models import CountryOffice

from .query import Query
from .report_template import ReportTemplate


class ChartPage(models.Model):
    country_office = models.ForeignKey(CountryOffice, on_delete=models.CASCADE)
    title = models.CharField(max_length=100, db_index=True)
    template = models.ForeignKey(ReportTemplate, blank=True, null=True, on_delete=models.SET_NULL)
    query = models.ForeignKey(Query, blank=True, null=True, on_delete=models.SET_NULL)
    params = models.JSONField(default=dict, null=False, blank=True)

    class Meta:
        ordering = ("title",)

    class Tenant:
        tenant_filter_field = "country_office"

    def save(self, *args, **kwargs):
        if not self.country_office_id:
            self.country_office = self.query.country_office
        if self.query and self.country_office != self.query.country_office:
            raise ValidationError("ChartPage and Query must belong to the same CountryOffice")

        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self):
        return reverse("office-chart", args=[self.country_office.slug, self.pk])
