from typing import Any, Dict, TYPE_CHECKING

from django.db import models
from django.db.models import QuerySet

from hope_country_report.state import state

from .exceptions import InvalidTenantError
from .utils import must_tenant

if TYPE_CHECKING:
    from ...types.django import AnyModel


class TenantManager(models.Manager["AnyModel"]):
    def must_tenant(self) -> bool:
        return must_tenant()

    def get_tenant_filter(self) -> "Dict[str, Any]":
        if not self.must_tenant():
            return {}
        tenant_filter_field = self.model.Tenant.tenant_filter_field
        if not tenant_filter_field:
            raise ValueError(
                f"Set 'tenant_filter_field' on {self} or override `get_queryset()` to enable queryset filtering"
            )
        if tenant_filter_field == "__all__":
            return {}
        if tenant_filter_field == "__none__":
            return {"pk__lt": -1}
        if not state.tenant:
            raise InvalidTenantError("State does not have any active tenant")
        return {tenant_filter_field: state.tenant.hope_id}

    def get_queryset(self) -> "QuerySet[AnyModel]":
        flt = self.get_tenant_filter()
        if flt:
            state.filters.append({self.model: str(flt)})
        return super().get_queryset().filter(**flt)


class TenantModel(models.Model):
    class Meta:
        abstract = True

    class Tenant:
        tenant_filter_field = None

    objects = TenantManager()
    #
    # def save(
    #     self,
    #     force_insert: bool = ...,
    #     force_update: bool = ...,
    #     using: Optional[str] = ...,
    #     update_fields: Optional[Iterable[str]] = ...,
    # ) -> None:
    #     t = getattr(self, self.Tenant.tenant_filter_field)
    #     assert conf.auth.get_allowed_tenants().filter(pk=t.pk).exists()
    #     super().save(force_insert, force_update, using, update_fields)
    #
    # def delete(self, using: Any = None, keep_parents: bool = False) -> Tuple[int, Dict[str, int]]:
    #     return 0, {}