from django.conf import settings
from django.conf.urls import include
from django.contrib import admin
from django.urls import path

from hope_country_report.apps.tenant.sites import TenantAdminSite

tenant_admin = TenantAdminSite()

urlpatterns = [
    # path("", include("hope_country_report.web.urls")),
    # path("", tenant_admin.sites.site.urls),
    path("t/", tenant_admin.urls),
    path("admin/", admin.site.urls),
    # path("<str:country_code>/admin/", tenant_admin.urls),
    path(r"security/", include("unicef_security.urls", namespace="security")),
    path(r"social/", include("social_django.urls", namespace="social")),
    path(r"accounts/", include("django.contrib.auth.urls")),
    path(r"adminactions/", include("adminactions.urls")),
    # path(r"power_query/", include("power_query.urls")),
]


if settings.DEBUG:  # pragma: no cover
    import debug_toolbar

    urlpatterns += [
        path(r"__debug__/", include(debug_toolbar.urls)),
    ]
