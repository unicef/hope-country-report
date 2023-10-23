from django.apps import AppConfig


class Config(AppConfig):
    name = __name__.rpartition(".")[0]
    verbose_name = "Core"

    def ready(self) -> None:
        from ...config.celery import app  # noqa
        from ...utils import flags  # noqa
