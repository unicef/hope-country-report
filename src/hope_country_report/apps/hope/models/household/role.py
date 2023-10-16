from django.db import models

from .._base import HopeModel
from .hh import Household
from .ind import Individual


class IndividualRoleInHousehold(HopeModel):
    individual = models.ForeignKey(Individual, on_delete=models.CASCADE, related_name="households_and_roles")
    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name="individuals_and_roles")
    role = models.CharField(max_length=255, blank=True)

    class Meta:
        unique_together = ("role", "household")
        db_table = "household_individualroleinhousehold"

    class Tenant:
        tenant_filter_field = "household__business_area"

    def __str__(self) -> str:
        return f"{self.individual.full_name} - {self.role}"
