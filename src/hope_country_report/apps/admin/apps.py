from django.apps import AppConfig


class Config(AppConfig):
    name = "hope_country_report.apps.admin"
    label = "report_admin"
    verbose_name = "Admin"
    default_site = "hope_country_report.apps.admin.sites.ReportAdminSite"
    default = True
