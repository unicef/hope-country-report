from django.db import models

from hope_country_report.apps.hope.models import HopeModel


class DataCollectingType(HopeModel):
    code = models.CharField(max_length=60, unique=True)
    description = models.TextField(blank=True)
    compatible_types = models.ManyToManyField("self", blank=True)

    class Meta:
        db_table = "core_datacollectingtype"

    def __str__(self) -> str:
        return f"{self.code} - {self.description}"