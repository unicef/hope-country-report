from django.conf import settings
from django.conf.urls import include
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import path

from tenant_admin.resolver import tenant_patterns
from tenant_admin.sites import TenantAdminSite
from tenant_admin.views import set_tenant

tenant_admin = TenantAdminSite()


def select_tenant(request):
    pass


urlpatterns = [
    path("", include("hope_country_report.web.urls")),
    path("", tenant_admin.urls),
    # path("t/", include(tenant_patterns(*tenant_admin.get_urls()),namespace="tenant_admin" )),
    path("admin/", admin.site.urls),
    # path("<str:country_code>/admin/", tenant_admin.urls),
    path(r"security/", include("unicef_security.urls", namespace="security")),
    path(r"social/", include("social_django.urls", namespace="social")),
    path(r"accounts/", include("django.contrib.auth.urls")),
    path(r"adminactions/", include("adminactions.urls")),
    path(r"power_query/", include("power_query.urls")),
]

# urlpatterns += [
#     path("settenant/", set_tenant, name="set_tenant"),
#     *tenant_patterns(*tenant_admin.get_urls(), namespace="tenant_admin", app_name="tenant_admin")
# ]

# if settings.DEBUG:  # pragma: no cover
#     import debug_toolbar
#
#     urlpatterns += [
#         path(r"__debug__/", include(debug_toolbar.urls)),
#     ]
