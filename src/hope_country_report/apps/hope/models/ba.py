from django.db import models

from hope_country_report.apps.hope.models._base import HopeModel
from hope_country_report.apps.tenant.utils import get_selected_tenant, is_tenant_active


class BusinessAreaManager(models.Manager):
    def get_queryset(self):
        if is_tenant_active():
            active_tenant = get_selected_tenant()
            return super().get_queryset().filter(id=active_tenant.hope_id)
        return super().get_queryset()


class BusinessArea(HopeModel):
    id = models.CharField(primary_key=True, max_length=100)
    name = models.CharField(max_length=100)
    active = models.BooleanField(default=False)
    code = models.CharField(max_length=10, unique=True)
    long_name = models.CharField(max_length=255)
    region_code = models.CharField(max_length=8)
    region_name = models.CharField(max_length=8)

    objects = BusinessAreaManager()

    class Meta:
        db_table = "core_businessarea"

    class Tenant:
        tenant_filter_field = "id"

    def __str__(self) -> str:
        return str(self.name)
