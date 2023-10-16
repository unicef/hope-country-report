from typing import Any, Dict, Iterable, Optional, Tuple

from django.db import models

from hope_country_report.apps.tenant.db import TenantModel


class TimeStampedUUIDModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        abstract = True


class HopeModel(TenantModel, models.Model):
    class Meta:
        abstract = True
        managed = False
        app_label = "hope"

    class Tenant:
        tenant_filter_field = None

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
