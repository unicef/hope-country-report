from django.db import models


class Household(models.Model):
    unicef_id = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    withdrawn = models.BooleanField(default=False, db_index=True)
    withdrawn_date = models.DateTimeField(null=True, blank=True, db_index=True)
    id = models.CharField(
        primary_key=True,
        max_length=100,
        editable=False,
    )

    class Meta:
        managed = False
        db_table = "household_household"
