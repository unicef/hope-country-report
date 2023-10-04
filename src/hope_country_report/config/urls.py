from django.conf import settings
from django.conf.urls import include
from django.contrib import admin
from django.urls import path

from tenant_admin.sites import TenantAdminSite

tenant_admin = TenantAdminSite()

urlpatterns = [
    path("", include("hope_country_report.web.urls")),
    path("", tenant_admin.urls),
    path("admin/", admin.site.urls),
    path(r"security/", include("unicef_security.urls", namespace="security")),
    path(r"social/", include("social_django.urls", namespace="social")),
    path(r"accounts/", include("django.contrib.auth.urls")),
    path(r"adminactions/", include("adminactions.urls")),
    path(r"power_query/", include("hope_country_report.apps.power_query.urls")),
]


if settings.DEBUG:  # pragma: no cover
    import debug_toolbar

    urlpatterns += [
        path(r"__debug__/", include(debug_toolbar.urls)),
    ]
