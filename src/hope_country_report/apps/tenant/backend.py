from typing import TYPE_CHECKING

from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import Permission

from hope_country_report.apps.tenant.utils import active_role_q, get_selected_tenant
from hope_country_report.state import state

if TYPE_CHECKING:
    from django.db import Model
    from django.db.models import QuerySet

    from hope_country_report.apps.core.models import CountryOffice, User
    from hope_country_report.types.django import _R, AnyModel, AnyUser


class TenantBackend(BaseBackend):
    model: "AnyModel" = None

    def get_all_permissions(self, user: "AnyUser", obj: "AnyModel|None" = None) -> set[str]:
        tenant: "CountryOffice|None" = state.tenant
        if not tenant:
            return set()
        if user.is_anonymous:
            return set()
        perm_cache_name = f"_tenant_{str(tenant.pk)}_perm_cache"
        if not hasattr(user, perm_cache_name):
            qs = Permission.objects.all()
            if not user.is_superuser:
                qs = qs.filter(group__userrole__user=user, group__userrole__country_office=tenant).filter(
                    active_role_q("group__userrole__")
                )
            perms = qs.values_list("content_type__app_label", "codename").order_by()
            setattr(user, perm_cache_name, {f"{ct}.{name}" for ct, name in perms})
        return getattr(user, perm_cache_name)

    def get_available_modules(self, user: "User") -> "set[str]":
        return {perm[: perm.index(".")] for perm in self.get_all_permissions(user)}

    def has_module_perms(self, user: "User", app_label: str) -> bool:
        tenant: "AnyModel" = get_selected_tenant()
        if not tenant:
            return False

        if user.is_superuser:
            return True
        return app_label in self.get_available_modules(user)

    def get_allowed_tenants(self, request: "_R|None" = None) -> "QuerySet[Model] | None":
        from .config import conf

        request = request or state.request
        allowed_tenants: "QuerySet[Model] | None"
        if request.user.is_superuser:
            allowed_tenants = conf.tenant_model.objects.all()
        elif request.user.is_authenticated:
            allowed_tenants = (
                conf.tenant_model.objects.filter(userrole__user=request.user)
                .filter(active_role_q("userrole__"))
                .distinct()
            )
        else:
            allowed_tenants = conf.tenant_model.objects.none()

        return allowed_tenants
