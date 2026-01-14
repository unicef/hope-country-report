from django.core.exceptions import ValidationError
from django.db import models

from hope_country_report.apps.core.models import CountryOffice
from hope_country_report.apps.power_query.models import Query


class Event(models.Model):
    name = models.CharField(max_length=255, unique=True)
    enabled = models.BooleanField(default=True, blank=True)
    office = models.ForeignKey(CountryOffice, on_delete=models.CASCADE, null=True, blank=True)
    query = models.OneToOneField(Query, on_delete=models.CASCADE, null=True)
    extras = models.JSONField(default=dict, blank=True)
    routing_key = models.CharField(max_length=255, default="hcr.dataset.save", blank=True)
    publish_as_url = models.BooleanField(
        default=False, blank=True, help_text="If true, event will contain a URL to the dataset instead of the data"
    )

    def __str__(self):
        return self.name

    def get_routing_key(self) -> str:
        return self.routing_key or f"hcr.{self.office.code.lower()}.dataset.save"

    def clean(self):
        """
        Ensures the Event's office matches the associated Query's country_office.
        """
        super().clean()
        if not self.query:
            return

        if self.query.country_office and not self.office:
            self.office = self.query.country_office

        if self.office != self.query.country_office:
            raise ValidationError(
                {
                    "office": f"The office '{self.office}' does not match the query's office "
                    f"'{self.query.country_office}'. Leave the office field blank to auto-populate it."
                }
            )
