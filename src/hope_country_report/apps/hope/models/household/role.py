from django.db import models

from .._base import HopeModel
from .hh import Household
from .ind import Individual

ROLE_PRIMARY = "PRIMARY"
ROLE_ALTERNATE = "ALTERNATE"
ROLE_NO_ROLE = "NO_ROLE"
ROLE_CHOICE = (
    (ROLE_NO_ROLE, "None"),
    (ROLE_ALTERNATE, "Alternate collector"),
    (ROLE_PRIMARY, "Primary collector"),
)


class IndividualRoleInHousehold(HopeModel):
    id = models.CharField(primary_key=True, max_length=100, editable=False)
    individual = models.ForeignKey(Individual, on_delete=models.CASCADE, related_name="households_and_roles")
    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name="individuals_and_roles")
    role = models.CharField(max_length=255, blank=True, choices=ROLE_CHOICE)

    class Meta:
        unique_together = ("role", "household")
        db_table = "household_individualroleinhousehold"

    class Tenant:
        tenant_filter_field = "household__business_area"

    def __str__(self) -> str:
        return f"{self.individual.full_name} - {self.role}"
