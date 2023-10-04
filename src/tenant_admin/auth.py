from typing import TYPE_CHECKING

from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import Permission
from django.db.models import QuerySet

# FIXME: use DIP here
# from hope_country_report.apps.core.models import CountryOffice
# from hope_country_report.apps.hope.models import BusinessArea
from hope_country_report.state import state

from .config import conf

if TYPE_CHECKING:
    from typing import Optional, TYPE_CHECKING

    from django.db import Model

    from hope_country_report.apps.core.models import User
    from hope_country_report.types.django import _M, _R


class BaseTenantAuth(BaseBackend):
    model: "_M" = None

    def get_selected_tenant(self) -> "_M":
        return conf.strategy.get_selected_tenant()

    def get_all_permissions(self, user: "User", obj: "_M|None" = None) -> set[str]:
        tenant: "_M" = self.get_selected_tenant()
        if not tenant:
            return []
        if user.is_anonymous:
            return []
        perm_cache_name = "_tenant_%s_perm_cache" % str(tenant.pk)
        if not hasattr(user, perm_cache_name):
            qs = Permission.objects.all()
            if not user.is_superuser:
                qs = qs.filter(
                    **{
                        "group__userrole__user": user,
                        "group__userrole__country_office": tenant,
                    }
                )
            perms = qs.values_list("content_type__app_label", "codename").order_by()
            setattr(user, perm_cache_name, {"%s.%s" % (ct, name) for ct, name in perms})
        return getattr(user, perm_cache_name)

    # def has_module_perms(self, user: "User", app_label: str) -> bool:
    #     tenant: "_M" = self.get_selected_tenant()
    #     if not tenant:
    #         return []
    #
    #     if user.is_superuser:
    #         return True
    #     return user.is_active and any(
    #         perm[: perm.index(".")] == app_label for perm in self.get_all_permissions(user)
    #     )

    def get_allowed_tenants(self, request: "_R|None" = None) -> "Optional[QuerySet[Model]]":
        from .config import conf

        request = request or state.request
        allowed_tenants: "Optional[QuerySet[Model]]"
        if request.user.is_superuser:
            allowed_tenants = conf.tenant_model.objects.all()
        elif request.user.is_authenticated:
            allowed_tenants = conf.tenant_model.objects.filter(userrole__user=request.user)
        else:
            allowed_tenants = conf.tenant_model.objects.none()

        return allowed_tenants

    # def get_allowed_tenants(self, request: "_R") -> "QuerySet[Model]":
    #     from .config import conf
    #     from hope_country_report.apps.core.models import CountryOffice
    #
    #     if not (allowed_tenants := getattr(request.user, "_allowed_tenants", None)):
    #         # related_field = get_field_to(self.model, conf.tenant_model)
    #         # related_query_field = related_field.related_query_name()
    #         # to_user = get_field_to(related_field.model, get_user_model())
    #         # permissions_query = "%s__%s" % (related_query_field, to_user.name)
    #         if request.user.is_authenticated:
    #             # allowed_tenants = conf.tenant_model.objects.filter(**{permissions_query: request.user})
    #             allowed_tenants = CountryOffice.objects.filter(userrole__user=request)
    #         else:
    #             allowed_tenants = conf.tenant_model.objects.none()
    #         request.user._allowed_tenants = allowed_tenants
    #     return request.user._allowed_tenants

    # def _find_fks(self):
    #     from tenant_admin.config import conf
    #
    #     opts: Options = self.model._meta
    #     u, g, t = None, None, None
    #     for field in opts.get_fields():
    #         if isinstance(field, ForeignKey):
    #             if field.related_model == conf.tenant_model:
    #                 t = field
    #             elif field.related_model == get_user_model():
    #                 u = field
    #             elif field.related_model == Group:
    #                 g = field
    #     return u, g, t
    #
    # def has_module_perms(self, request, app_label):
    #     """
    #     Return True if user_obj has any permissions in the given app_label.
    #     """
    #     return request.user.is_active and any(
    #         perm[: perm.index(".")] == app_label for perm in self.get_all_permissions(request)
    #     )
    #
    # def get_all_permissions(self, request: "_R", obj: "_M|None" = None):
    #     perm_cache_name = "_tenant_%s_perm_cache" % str(conf.strategy.get_selected_tenant(request))
    #     if not hasattr(request.user, perm_cache_name):
    #         user_field, group_field, tenant_field = self._find_fks()
    #         user_groups_query = "%s__%s__%s" % (
    #             group_field.name,
    #             group_field.related_query_name(),
    #             user_field.name,
    #         )
    #         perms = Permission.objects.filter(**{user_groups_query: request.user})
    #
    #         perms = perms.values_list("content_type__app_label", "codename").order_by()
    #         setattr(
    #             request.user,
    #             perm_cache_name,
    #             {"%s.%s" % (ct, name) for ct, name in perms},
    #         )
    #     return getattr(request.user, perm_cache_name)
