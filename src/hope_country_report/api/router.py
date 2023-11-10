from django.conf import settings

from rest_framework_nested import routers

from . import views

if settings.DEBUG:
    router = routers.DefaultRouter()
else:
    router = routers.SimpleRouter()

router.register(r"offices", views.CountryOfficeViewSet)

office_router = routers.NestedSimpleRouter(router, "offices", lookup="office")
office_router.register(r"queries", views.QueryDataViewSet, basename="office-queries")
