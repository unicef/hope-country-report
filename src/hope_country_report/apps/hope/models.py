from django.db import models
from model_utils.fields import UUIDField


class Household(models.Model):
    unicef_id = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    withdrawn = models.BooleanField(default=False, db_index=True)
    withdrawn_date = models.DateTimeField(null=True, blank=True, db_index=True)
    id = UUIDField(
        primary_key=True,
        version=4,
        editable=False,
    )

    class Meta:
        managed = False
        db_table = "household_household"
