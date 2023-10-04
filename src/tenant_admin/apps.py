from django.apps import AppConfig


class Config(AppConfig):
    name = "tenant_admin"
    verbose_name = "Admin"

    def ready(self) -> None:
        from . import monkeypatch  # noqa
