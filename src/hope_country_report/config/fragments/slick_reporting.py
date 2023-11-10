from datetime import datetime

from django.utils import timezone

SLICK_REPORTING_SETTINGS = {
    "JQUERY_URL": "https://code.jquery.com/jquery-3.7.0.min.js",
    "DEFAULT_START_DATE_TIME": datetime(
        datetime.now().year, 1, 1, 0, 0, 0, tzinfo=timezone.utc
    ),  # Default: 1st Jan of current year
    "DEFAULT_END_DATE_TIME": datetime.datetime.today(),  # Default to today
    # "DEFAULT_CHARTS_ENGINE": SLICK_REPORTING_DEFAULT_CHARTS_ENGINE,
    "MEDIA": {
        "override": False,  # set it to True to override the media files,
        # False will append the media files to the existing ones.
        "js": (
            "https://cdn.jsdelivr.net/momentjs/latest/moment.min.js",
            "https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/js/select2.min.js",
            "https://cdn.datatables.net/1.13.4/js/jquery.dataTables.min.js",
            "https://cdn.datatables.net/1.13.4/js/dataTables.bootstrap5.min.js",
            "slick_reporting/slick_reporting.js",
            "slick_reporting/slick_reporting.report_loader.js",
            "slick_reporting/slick_reporting.datatable.js",
        ),
        "css": {
            "all": (
                "https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/css/select2.min.css",
                "https://cdn.datatables.net/1.13.4/css/dataTables.bootstrap5.min.css",
            )
        },
    },
    "FONT_AWESOME": {
        "CSS_URL": "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css",
        "ICONS": {
            "pie": "fas fa-chart-pie",
            "bar": "fas fa-chart-bar",
            "line": "fas fa-chart-line",
            "area": "fas fa-chart-area",
            "column": "fas fa-chart-column",
        },
    },
    "CHARTS": {
        "highcharts": "$.slick_reporting.highcharts.displayChart",
        "chartjs": "$.slick_reporting.chartjs.displayChart",
    },
    "MESSAGES": {
        "total": "Total",
    },
}
