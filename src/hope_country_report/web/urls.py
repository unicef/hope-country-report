from django.contrib.auth.views import LoginView
from django.urls import path

from .views import (
    download,
    index,
    OfficeDocumentDisplayView,
    OfficeDocumentDownloadView,
    OfficeHomeView,
    OfficeReportDetailView,
    OfficeReportListView,
    select_tenant,
    UserProfileView,
)

urlpatterns = [
    path("", index, name="index"),
    path(r"media/<path:path>", download, name="download-media"),
    path("login/", LoginView.as_view(), name="login"),
    path("profile/", UserProfileView.as_view(), name="profile"),
    path("select-tenant/", select_tenant, name="select-tenant"),
    path("<slug:co>/", OfficeHomeView.as_view(), name="office-index"),
    path("<slug:co>/reports/", OfficeReportListView.as_view(), name="office-reports"),
    path("<slug:co>/reports/<int:pk>/", OfficeReportDetailView.as_view(), name="office-report"),
    path(
        "<slug:co>/reports/<int:report>/document/<int:pk>/view/",
        OfficeDocumentDisplayView.as_view(),
        name="office-doc-display",
    ),
    path(
        "<slug:co>/reports/<int:report>/document/<int:pk>/download/",
        OfficeDocumentDownloadView.as_view(),
        name="office-doc-download",
    ),
]
