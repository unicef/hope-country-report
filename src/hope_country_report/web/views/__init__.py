from .charts import ChartDetailView, ChartListView  # noqa
from .document import (  # noqa
    OfficeDocumentDisplayView,
    OfficeDocumentDownloadView,
    OfficeReportDocumentDetailView,
    OfficeReportDocumentListView,
    RequestAccessView,
)
from .generic import (  # noqa
    download,
    index,
    OfficeHomeView,
    OfficeMapView,
    OfficePageListView,
    OfficePreferencesView,
    select_tenant,
)
from .report import OfficeConfigurationDetailView, OfficeConfigurationListView  # noqa
from .user import UserProfileView  # noqa
