from django.apps import AppConfig

from smart_admin.decorators import smart_register


class Config(AppConfig):
    name = "hope_country_report.apps.admin"
    label = "report_admin"
    verbose_name = "Admin"
    default_site = "hope_country_report.apps.admin.sites.ReportAdminSite"
    default = True
