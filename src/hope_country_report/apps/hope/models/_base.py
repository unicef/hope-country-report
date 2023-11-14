from typing import Any

from collections.abc import Iterable

from django.db import models

from hope_country_report.apps.tenant.db import TenantModel


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        abstract = True


class HopeModel(TenantModel, models.Model):
    id = models.CharField(primary_key=True, max_length=100, editable=False)

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
        using: str | None = ...,
        update_fields: Iterable[str] | None = ...,
    ) -> None:
        pass

    def delete(self, using: Any = None, keep_parents: bool = False) -> tuple[int, dict[str, int]]:
        return 0, {}
