from typing import Optional, TYPE_CHECKING

from hope_country_report.apps.hope.models import BusinessArea
from tenant_admin.auth import BaseTenantAuth

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from hope_country_report.types.http import AuthHttpRequest


class Auth(BaseTenantAuth):
    def get_allowed_tenants(self, request: "AuthHttpRequest") -> "Optional[QuerySet[BusinessArea]]":  # type: ignore
        from tenant_admin.config import conf

        allowed_tenants: "Optional[QuerySet[BusinessArea]]"
        if not (allowed_tenants := getattr(request.user, "_allowed_tenants", None)):
            # related_field = get_field_to(self.model, conf.tenant_model)
            # related_query_field = related_field.related_query_name()
            # to_user = get_field_to(related_field.model, get_user_model())
            # permissions_query = "%s__%s" % (related_query_field, to_user.name)
            if request.user.is_authenticated:
                # allowed_tenants = conf.tenant_model.objects.filter(**{permissions_query: request.user})
                # allowed_tenants = conf.tenant_model.objects.all()
                ids = list(request.user.userrole.values_list("business_area", flat=True))
                allowed_tenants = BusinessArea.objects.filter(id__in=ids)
            else:
                allowed_tenants = conf.tenant_model.objects.none()  # type: ignore
            request.user._allowed_tenants = allowed_tenants

        return allowed_tenants
