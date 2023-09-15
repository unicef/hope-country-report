from power_query.models import Query
from tenant_admin.options import TenantModelAdmin


class QueryAdmin(TenantModelAdmin):
    model = Query
    tenant_filter_field = "__none__"
    # search_fields = ("full_name",)
    # list_filter = (("household__unicef_id", ValueFilter), "relationship")
