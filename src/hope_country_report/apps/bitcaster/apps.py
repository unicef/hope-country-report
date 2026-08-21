from django.apps import AppConfig as BaseAppConfig


class AppConfig(BaseAppConfig):
    name = "hope_country_report.apps.bitcaster"
    verbose_name = "Bitcaster"

    def ready(self) -> None:
        from . import handlers  # noqa
