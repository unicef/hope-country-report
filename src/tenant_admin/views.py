from urllib.parse import urlsplit

from django.http import HttpResponse, HttpResponseRedirect
from django.utils.http import url_has_allowed_host_and_scheme

from tenant_admin.config import conf
from tenant_admin.utils import get_tenant_from_path, replace_tenant, tenantize_url

TENANT_QUERY_PARAMETER = "tenant"
TENANT_COOKIE_NAME = "tenant"


def set_tenant(request):
    next_url = request.POST.get("next", request.GET.get("next"))
    if (next_url or request.accepts("text/html")) and not url_has_allowed_host_and_scheme(
        url=next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        next_url = request.META.get("HTTP_REFERER")
        if not url_has_allowed_host_and_scheme(
            url=next_url,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        ):
            next_url = "/"
    response = HttpResponseRedirect(next_url) if next_url else HttpResponse(status=204)
    if request.method == "POST":
        tenant_pk = request.POST.get(TENANT_QUERY_PARAMETER)
        selected_tenant = conf.auth.get_allowed_tenants().get(pk=tenant_pk)
        if selected_tenant:
            next_path = urlsplit(next_url).path or "/"
            current_tenant = get_tenant_from_path(next_path)
            if current_tenant:
                next_trans = replace_tenant(next_path, selected_tenant.slug)
            else:
                next_trans = tenantize_url(next_path, selected_tenant.slug)
            if next_trans != next_path:
                response = HttpResponseRedirect(next_trans)
        response.set_cookie(TENANT_COOKIE_NAME, selected_tenant.slug)
    return response
