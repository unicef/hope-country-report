from django.apps import AppConfig


class Config(AppConfig):
    name = __name__.rpartition(".")[0]
    verbose_name = "PQ"

    def ready(self) -> None:
        from . import admin_t  # noqa
