from django.urls import include, path

from .router import office_router, router

urlpatterns = [
    path("", include(router.urls)),
    path("", include(office_router.urls)),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
]
