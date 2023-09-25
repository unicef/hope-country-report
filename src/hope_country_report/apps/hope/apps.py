from django.apps import AppConfig


class Config(AppConfig):
    name = __name__.rpartition(".")[0]
    verbose_name = "HOPE"

    def ready(self) -> None:
        from . import admin_t  # noqa

        # from hope_country_report.config.urls import tenant_admin
        # from hope_country_report.apps.hope.models import BusinessArea
        # tenant_admin.register(BusinessArea)
        # from ..tenant.sites import add_to_site
        # from .models import Program
        # add_to_site(Program)
