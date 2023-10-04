import functools

from django.urls import get_resolver, path

from tenant_admin.resolver import TenantPrefixPattern
from tenant_admin.views import set_tenant


@functools.lru_cache(maxsize=None)
def is_tenant_prefix_patterns_used(urlconf):
    for url_pattern in get_resolver(urlconf).url_patterns:
        if isinstance(url_pattern.pattern, TenantPrefixPattern):
            return True
    return False


urlpatterns = [
    path("settenant/", set_tenant, name="set_tenant"),
]
