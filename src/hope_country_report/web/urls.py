from django.contrib.auth.views import LoginView
from django.http import HttpResponse
from django.urls import path
from django.views.generic import TemplateView

from .views import (
    download,
    index,
    OfficeConfigurationDetailView,
    OfficeConfigurationListView,
    OfficeDocumentDisplayView,
    OfficeDocumentDownloadView,
    OfficeHomeView,
    OfficeMapView,
    OfficePageListView,
    OfficePreferencesView,
    OfficeReportDocumentDetailView,
    OfficeReportDocumentListView,
    RequestAccessView,
    select_tenant,
    UserProfileView,
)
from .views.base import OfficeTemplateView
from .views.charts import ChartDetailView, ChartListView

urlpatterns = [
    path("", index, name="index"),
    path("media/<path:path>", download, name="download-media"),
    path("login/", LoginView.as_view(), name="login"),
    path("profile/", UserProfileView.as_view(), name="user-profile"),
    path("select-tenant/", select_tenant, name="select-tenant"),
    path("<slug:co>/request-access/<int:id>/", RequestAccessView.as_view(), name="request-access"),
    path("<slug:co>/", OfficeHomeView.as_view(), name="office-index"),
    path("<slug:co>/map/", OfficeMapView.as_view(), name="office-map"),
    path("<slug:co>/charts/", ChartListView.as_view(), name="office-chart-list"),
    path("<slug:co>/charts/<int:pk>/", ChartDetailView.as_view(), name="office-chart"),
    path("<slug:co>/world/", OfficeTemplateView.as_view(template_name="web/office/world.html"), name="office-world"),
    # path("<slug:co>/users/", OfficeUserListView.as_view(), name="office-users"),
    path("<slug:co>/pages/", OfficePageListView.as_view(), name="office-pages"),
    path("<slug:co>/preferences/", OfficePreferencesView.as_view(), name="office-preferences"),
    path("<slug:co>/configurations/", OfficeConfigurationListView.as_view(), name="office-config-list"),
    path("<slug:co>/configuration/<int:pk>/", OfficeConfigurationDetailView.as_view(), name="office-config"),
    path("<slug:co>/docs/", OfficeReportDocumentListView.as_view(), name="office-doc-list"),
    path("<slug:co>/doc/<int:pk>/", OfficeReportDocumentDetailView.as_view(), name="office-doc"),
    path("<slug:co>/doc/<int:pk>/view/", OfficeDocumentDisplayView.as_view(), name="office-doc-display"),
    path("<slug:co>/doc/<int:pk>/download/", OfficeDocumentDownloadView.as_view(), name="office-doc-download"),
    path("errors/404/", TemplateView.as_view(template_name="404.html")),
    path("errors/403/", TemplateView.as_view(template_name="403.html")),
    path("health/", lambda request: HttpResponse("OK")),
]
