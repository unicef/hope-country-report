from django.conf.urls import include
from django.contrib import admin
from django.urls import path

import debug_toolbar

urlpatterns = [
    path("api/", include("hope_country_report.api.urls", namespace="api")),
    path("admin/", admin.site.urls),
    path("s2/", include("django_select2.urls")),
    path(r"security/", include("unicef_security.urls", namespace="security")),
    path(r"social/", include("social_django.urls", namespace="social")),
    path(r"accounts/", include("django.contrib.auth.urls")),
    path(r"adminactions/", include("adminactions.urls")),
    # path(r"pq/", include("hope_country_report.apps.power_query.urls")),
    path("silk/", include("silk.urls", namespace="silk")),
    path(r"__debug__/", include(debug_toolbar.urls)),
    path("", include("hope_country_report.web.urls")),
]
