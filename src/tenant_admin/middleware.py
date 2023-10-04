from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import get_script_prefix, is_valid_path
from django.utils.deprecation import MiddlewareMixin

from hope_country_report.state import state
from tenant_admin.urls import is_tenant_prefix_patterns_used
from tenant_admin.utils import get_tenant_from_path


class TenantAdminMiddleware(MiddlewareMixin):
    response_redirect_class = HttpResponseRedirect

    def process_request(self, request):
        tenant = get_tenant_from_path(request.path)
        state.tenant = tenant

    def process_response(self, request, response):
        tenant = state.tenant
        tenant_from_path = get_tenant_from_path(request.path_info)
        urlconf = getattr(request, "urlconf", settings.ROOT_URLCONF)
        tenant_patterns_used = is_tenant_prefix_patterns_used(urlconf)

        if response.status_code == 404 and not tenant_from_path and tenant_patterns_used:
            # Maybe the language code is missing in the URL? Try adding the
            # language prefix and redirecting to that URL.
            tenant_path = "/%s%s" % (tenant, request.path_info)
            path_valid = is_valid_path(tenant_path, urlconf)
            path_needs_slash = not path_valid and (
                settings.APPEND_SLASH and not tenant_path.endswith("/") and is_valid_path("%s/" % tenant_path, urlconf)
            )

            if path_valid or path_needs_slash:
                script_prefix = get_script_prefix()
                # Insert language after the script prefix and before the
                # rest of the URL
                tenant_url = request.get_full_path(force_append_slash=path_needs_slash).replace(
                    script_prefix, "%s%s/" % (script_prefix, tenant), 1
                )
                # Redirect to the language-specific URL as detected by
                # get_language_from_request(). HTTP caches may cache this
                # redirect, so add the Vary header.
                redirect = self.response_redirect_class(tenant_url)
                return redirect
        return response
