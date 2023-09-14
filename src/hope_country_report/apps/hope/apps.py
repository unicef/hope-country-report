from django.apps import AppConfig as BaseAppConfig


class AppConfig(BaseAppConfig):
    name = __name__.rpartition(".")[0]
    verbose_name = "HOPE"

    def ready(self) -> None:
        from . import admin_t  # noqa
