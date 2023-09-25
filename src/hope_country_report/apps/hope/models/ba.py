from django.db import models

from hope_country_report.apps.hope.models._base import HopeModel


class BusinessArea(HopeModel):
    id = models.CharField(primary_key=True, max_length=100)
    name = models.CharField(max_length=100)
    active = models.BooleanField(default=False)
    code = models.CharField(max_length=10, unique=True)
    long_name = models.CharField(max_length=255)
    region_code = models.CharField(max_length=8)
    region_name = models.CharField(max_length=8)

    class Meta:
        db_table = "core_businessarea"

    def __str__(self) -> str:
        return str(self.name)
