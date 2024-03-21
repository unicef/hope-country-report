from .charts import ChartDetailView, ChartListView
from .document import (
    OfficeDocumentDisplayView,
    OfficeDocumentDownloadView,
    OfficeReportDocumentDetailView,
    OfficeReportDocumentListView,
    RequestAccessView,
)
from .generic import (
    download,
    image_proxy_view,
    index,
    OfficeHomeView,
    OfficeMapView,
    OfficePageListView,
    OfficePreferencesView,
    select_tenant,
)
from .report import OfficeConfigurationDetailView, OfficeConfigurationListView
from .user import UserProfileView
