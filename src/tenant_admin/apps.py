from django.apps import AppConfig


class Config(AppConfig):
    name = "tenant_admin"

    def ready(self) -> None:
        from . import checks  # noqa
        from .options import model_admin_registry
        from .sites import site

        for __, opt in model_admin_registry.items():
            site.register(opt)
