from django.contrib.admin.apps import SimpleAdminConfig
from django.utils.functional import classproperty


class Config(SimpleAdminConfig):
    verbose_name = "Admin"
    default = True

    def ready(self) -> None:
        from django.contrib.admin import autodiscover

        autodiscover()

    @classproperty
    def default_site(self) -> str:
        return "hope_country_report.apps.admin.sites.HRAdminSite"
