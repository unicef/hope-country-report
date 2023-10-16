from django.db import models

from ._base import HopeModel


class DataCollectingType(HopeModel):
    code = models.CharField(max_length=60, unique=True)
    description = models.TextField(blank=True)
    compatible_types = models.ManyToManyField("self", blank=True)

    class Meta:
        db_table = "program_datacollectingtype"

    class Tenant:
        tenant_filter_field = "__all__"

    def __str__(self) -> str:
        return f"{self.code} - {self.description}"
