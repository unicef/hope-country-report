from django.db import models

from hope_country_report.apps.hope.models import HopeModel


class Program(HopeModel):
    id = models.CharField(primary_key=True, max_length=100, editable=False)
    name = models.CharField(max_length=100)
    # active = models.BooleanField(default=False)
    # data_collecting_type = models.ForeignKey(
    #     DataCollectingType, related_name="programs", on_delete=models.PROTECT, null=True, blank=True
    # )
    business_area = models.ForeignKey("BusinessArea", on_delete=models.CASCADE)

    class Meta:
        db_table = "program_program"

    def __str__(self) -> str:
        return str(self.name)
