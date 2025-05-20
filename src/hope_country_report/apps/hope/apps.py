from django.apps import AppConfig

from hope_country_report.state import state


class Config(AppConfig):
    name = __name__.rpartition(".")[0]
    verbose_name = "HOPE"

    def ready(self) -> None:
        from .patcher import patch

        if not state.inspecting:  # pragma: no branch
            patch()
