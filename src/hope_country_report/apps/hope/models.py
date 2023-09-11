from typing import Any, Dict, Iterable, Optional, Tuple

from django.db import models


class HopeModel(models.Model):
    class Meta:
        abstract = True
        managed = False

    def save(
        self,
        force_insert: bool = ...,
        force_update: bool = ...,
        using: Optional[str] = ...,
        update_fields: Optional[Iterable[str]] = ...,
    ) -> None:
        pass

    def delete(self, using: Any = None, keep_parents: bool = False) -> Tuple[int, Dict[str, int]]:
        return 0, {}


class BusinessArea(HopeModel):
    id = models.CharField(primary_key=True, max_length=100, editable=False)
    name = models.CharField(max_length=100, editable=False)

    class Meta:
        db_table = "core_businessarea"


class Household(HopeModel):
    unicef_id = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    withdrawn = models.BooleanField(default=False, db_index=True)
    withdrawn_date = models.DateTimeField(null=True, blank=True, db_index=True)
    id = models.CharField(primary_key=True, max_length=100, editable=False)

    class Meta:
        db_table = "household_household"


class Individual(HopeModel):
    unicef_id = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    id = models.CharField(primary_key=True, max_length=100, editable=False)

    class Meta:
        db_table = "household_individual"
