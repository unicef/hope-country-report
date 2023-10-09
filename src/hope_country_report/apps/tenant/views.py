# from django.http import HttpResponse, HttpResponseRedirect
# from django.utils.http import url_has_allowed_host_and_scheme
#
# from .config import conf
# from .utils import set_selected_tenant
# from ...types.http import AuthHttpRequest
#
# TENANT_QUERY_PARAMETER = "tenant"
# TENANT_COOKIE_NAME = "tenant"
#
#
# def set_tenant(request: "AuthHttpRequest"):
#     next_url = request.POST.get("next", request.GET.get("next"))
#     if (next_url or request.accepts("text/html")) and not url_has_allowed_host_and_scheme(
#         url=next_url,
#         allowed_hosts={request.get_host()},
#         require_https=request.is_secure(),
#     ):
#         next_url = request.META.get("HTTP_REFERER")
#         if not url_has_allowed_host_and_scheme(
#             url=next_url,
#             allowed_hosts={request.get_host()},
#             require_https=request.is_secure(),
#         ):
#             next_url = "/"
#     # next_url = "/"
#     response = HttpResponseRedirect(next_url) if next_url else HttpResponse(status=204)
#     if request.method == "POST":
#         tenant_pk = request.POST.get(TENANT_QUERY_PARAMETER)
#         selected_tenant = conf.auth.get_allowed_tenants().get(pk=tenant_pk)
#         if selected_tenant:
#             set_selected_tenant(selected_tenant)
#             # state.tenant = selected_tenant.slug
#             # response.set_cookie(conf.COOKIE_NAME, selected_tenant.slug)
#     return response
