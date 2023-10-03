# from typing import Any, Optional, TYPE_CHECKING
#
# from django.contrib.auth.models import Permission
#
# from hope_country_report.apps.core.models import CountryOffice
# from hope_country_report.apps.hope.models import BusinessArea
# from tenant_admin.auth import BaseTenantAuth
# from tenant_admin.config import conf
#
# if TYPE_CHECKING:
#     from django.db.models import QuerySet
#
#     from hope_country_report.types.http import _M, _R, AuthHttpRequest
#
#
# class Auth(BaseTenantAuth):
#     model = BusinessArea
#
#     def get_all_permissions(self, request: "_R", obj: "_M|None" = None) -> Any:
#         perm_cache_name = "_tenant_%s_perm_cache" % str(conf.strategy.get_selected_tenant(request))
#         if not hasattr(request.user, perm_cache_name):
#             # user_field, group_field, tenant_field = self._find_fks()
#             # print(user_field, group_field, tenant_field )
#             # user_groups_query = "%s__%s__%s" % (
#             #     group_field.name,
#             #     group_field.related_query_name(),
#             #     user_field.name,
#             # )
#             qs = Permission.objects.all()
#             if not request.user.is_superuser:
#                 qs = qs.filter(**{"group__userrole__user": request.user})
#             # perms = Permission.objects.filter(**{"group__userrole__user": request.user})
#
#             perms = qs.values_list("content_type__app_label", "codename").order_by()
#             setattr(request.user, perm_cache_name, {"%s.%s" % (ct, name) for ct, name in perms})
#         return getattr(request.user, perm_cache_name)
#
#     def has_module_perms(self, request: "AuthHttpRequest", app_label: str) -> bool:
#         """
#         Return True if user_obj has any permissions in the given app_label.
#         """
#         if request.user.is_superuser:
#             return True
#         return request.user.is_active and any(
#             perm[: perm.index(".")] == app_label for perm in self.get_all_permissions(request)
#         )
#
#     def get_allowed_tenants(self, request: "AuthHttpRequest") -> "Optional[QuerySet[BusinessArea]]":
#         from tenant_admin.config import conf
#
#         allowed_tenants: "Optional[QuerySet[BusinessArea]]"
#         if not (allowed_tenants := getattr(request.user, "_allowed_tenants", None)):
#             # related_field = get_field_to(self.model, conf.tenant_model)
#             # related_query_field = related_field.related_query_name()
#             # to_user = get_field_to(related_field.model, get_user_model())
#             # permissions_query = "%s__%s" % (related_query_field, to_user.name)
#             if request.user.is_superuser:
#                 allowed_tenants = CountryOffice.objects.all()
#             elif request.user.is_authenticated:
#                 # allowed_tenants = conf.tenant_model.objects.filter(**{permissions_query: request.user})
#                 # allowed_tenants = conf.tenant_model.objects.all()
#                 allowed_tenants = CountryOffice.objects.filter(userrole__user=request.user)
#
#                 # allowed_tenants = BusinessArea.objects.filter(id__in=ids)
#             else:
#                 allowed_tenants = conf.tenant_model.objects.none()
#             request.user._allowed_tenants = allowed_tenants
#
#         return allowed_tenants
