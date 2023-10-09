from django.conf import settings
from django.conf.urls import include
from django.contrib import admin
from django.urls import path

urlpatterns = [
    # path("", include("hope_country_report.web.urls")),
    path(r"security/", include("unicef_security.urls", namespace="security")),
    path(r"social/", include("social_django.urls", namespace="social")),
    path(r"accounts/", include("django.contrib.auth.urls")),
    path(r"adminactions/", include("adminactions.urls")),
    path(r"power_query/", include("hope_country_report.apps.power_query.urls")),
    path("silk/", include("silk.urls", namespace="silk")),
]

if settings.DEBUG:  # pragma: no cover
    import debug_toolbar

    urlpatterns += [
        path(r"__debug__/", include(debug_toolbar.urls)),
    ]
# if settings.TENANT_IS_MASTER:
#     # admin_site = admin.site
#     # admin.site.site_title = "HOPE Reporting"
#     # admin.site.site_header = "HOPE Reporting"
#     # admin.site.index_title = "HOPE Reporting"
#     # admin.site.final_catch_all_view = False
urlpatterns += [path("", admin.site.urls)]
# else:
#     tenant_admin = TenantAdminSite()
#     urlpatterns += [path("", tenant_admin.urls)]
