from django.http import HttpResponse, HttpResponseRedirect
from django.urls import translate_url
from django.utils.http import url_has_allowed_host_and_scheme

from tenant_admin.utils import tenantize_url

TENANT_QUERY_PARAMETER = "tenant"
TENANT_COOKIE_NAME = "tenant"


def set_tenant(request):
    """
    Redirect to a given URL while setting the chosen language in the session
    (if enabled) and in a cookie. The URL and the language code need to be
    specified in the request parameters.

    Since this view changes how the user will see the rest of the site, it must
    only be accessed as a POST request. If called as a GET request, it will
    redirect to the page in the request (the 'next' parameter) without changing
    any state.
    """
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
        from hope_country_report.apps.core.models import CountryOffice

        tenant = CountryOffice.objects.get(pk=tenant_pk)
        if tenant:
            if next_url:
                next_trans = tenantize_url(next_url, tenant.code)
                if next_trans != next_url:
                    response = HttpResponseRedirect(next_trans)

        print("set_tenant", 11111111, tenant_pk, tenant.code, response.url)
        # response.set_cookie(TENANT_COOKIE_NAME, tenant.code)
    return response
