from typing import Any, Dict, TYPE_CHECKING, TypeVar

from django.db import models
from django.db.models import Model, QuerySet

from hope_country_report.state import state

from .exceptions import InvalidTenantError
from .utils import get_selected_tenant, is_tenant_active

if TYPE_CHECKING:
    _T = TypeVar("_T", bound=Model, covariant=True)


class TenantManager(models.Manager):
    def get_tenant_filter(self) -> "Dict[str, Any]":
        if not is_tenant_active():
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
        active_tenant = get_selected_tenant()
        if not active_tenant:
            raise InvalidTenantError
        return {tenant_filter_field: active_tenant.hope_id}

    def get_queryset(self) -> "QuerySet[_T]":
        flt = self.get_tenant_filter()
        state.filters.append(str(flt))
        return super().get_queryset().filter(**flt)


class TenantModel(models.Model):
    class Meta:
        abstract = True

    class Tenant:
        tenant_filter_field = None

    # objects = TenantManager()
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
