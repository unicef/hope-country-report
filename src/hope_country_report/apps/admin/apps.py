from django.contrib.admin.apps import SimpleAdminConfig


class Config(SimpleAdminConfig):
    verbose_name = "Admin"
    default = True
    default_site = "hope_country_report.apps.admin.sites.HRAdminSite"

    def ready(self) -> None:
        from django.contrib.admin import autodiscover

        autodiscover()
