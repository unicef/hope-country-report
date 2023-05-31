from django.apps import AppConfig as BaseAppConfig

from smart_admin.decorators import smart_register


class AppConfig(BaseAppConfig):
    name = __name__.rpartition(".")[0]
    verbose_name = "Core"

    def ready(self) -> None:
        super().ready()
        from django.contrib.contenttypes.models import ContentType

        from smart_admin.smart_auth.admin import ContentTypeAdmin

        smart_register(ContentType)(ContentTypeAdmin)
