from django.db import models

from hope_country_report.apps.hope.models import HopeModel


class Program(HopeModel):
    id = models.CharField(primary_key=True, max_length=100, editable=False)
    name = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    start_date = models.DateField(db_index=True)
    end_date = models.DateField(db_index=True)
    description = models.CharField(max_length=255)
    business_area = models.ForeignKey("BusinessArea", on_delete=models.CASCADE)
    sector = models.CharField(max_length=50, db_index=True)
    data_collecting_type = models.ForeignKey("DataCollectingType", related_name="programs", on_delete=models.PROTECT)

    class Meta:
        db_table = "program_program"

    class Tenant:
        tenant_filter_field = "business_area"

    def __str__(self) -> str:
        return str(self.name)


class Cycle(HopeModel):
    id = models.CharField(primary_key=True, max_length=100, editable=False)
    status = models.CharField(max_length=10, db_index=True)
    start_date = models.DateField()  # first from program
    end_date = models.DateField(null=True, blank=True)
    program = models.ForeignKey("Program", on_delete=models.CASCADE, related_name="cycles")

    class Meta:
        db_table = "program_programcycle"

    class Tenant:
        tenant_filter_field = "program__business_area"

    def __str__(self) -> str:
        return str(self.name)
