from typing import TYPE_CHECKING

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import Permission

from hope_country_report.apps.power_query.exceptions import RequestablePermissionDenied
from hope_country_report.apps.power_query.models import ReportDocument

if TYPE_CHECKING:
    from django.db.models import Model

    from hope_country_report.apps.hope.models import HopeModel
    from hope_country_report.types.django import AnyModel, AnyUser


class PowerQueryBackend(ModelBackend):
    def _get_role_permissions(self, user_obj: "AnyUser", obj: "Model | HopeModel"):
        if not user_obj.is_active or user_obj.is_anonymous or obj is None or user_obj.is_superuser:
            return set()
        if obj._meta.app_label == "power_query" and getattr(obj, "country_office", None):
            co = obj.country_office
            perm_cache_name = f"_power_query_{co.pk}_perm_cache"
            if not hasattr(user_obj, perm_cache_name):
                perms = Permission.objects.filter(
                    group__userrole__user=user_obj, group__userrole__country_office=obj.country_office
                )
                perms = perms.values_list("content_type__app_label", "codename").order_by()
                setattr(user_obj, perm_cache_name, {f"{ct}.{name}" for ct, name in perms})
            return getattr(user_obj, perm_cache_name)
        return set()

    def get_all_permissions(self, user_obj: "AnyUser", obj: "AnyModel|None" = None) -> set[str]:
        return {
            *super().get_all_permissions(user_obj, obj),
            *self._get_role_permissions(user_obj, obj=obj),
        }

    def has_perm(self, user_obj: "AnyUser", perm: str, obj: "AnyModel|None" = None) -> bool:
        if user_obj.is_active and user_obj.is_superuser:
            return True

        if user_obj.is_authenticated and obj and obj._meta.app_label == "power_query":
            if getattr(obj, "owner", None) and user_obj == obj.owner:
                return True
            if isinstance(obj, ReportDocument):
                if user_obj == obj.report.owner:
                    return True
                if (
                    obj.report.limit_access_to.count()
                    and not obj.report.limit_access_to.filter(id=user_obj.id).exists()
                ):
                    raise RequestablePermissionDenied(obj.report)
            else:
                return perm in self.get_all_permissions(user_obj, obj)
        return super().has_perm(user_obj, perm, obj)
