from typing import Any, TYPE_CHECKING
import json

from django.core.checks import Warning, register
from django.db.utils import OperationalError, ProgrammingError

if TYPE_CHECKING:
    from django.apps import AppConfig


@register()
def check_periodic_tasks(app_configs: "AppConfig | None" = None, **kwargs: Any) -> list[Warning]:
    warnings = []
    try:
        from django_celery_beat.models import PeriodicTask

        invalid_tasks = PeriodicTask.objects.filter(
            task="hope_country_report.apps.power_query.celery_tasks.refresh_report"
        )
        for task in invalid_tasks:
            has_report_id = False
            try:
                args = json.loads(task.args) if task.args else []
                kwargs_dict = json.loads(task.kwargs) if task.kwargs else {}
                if args or "report_id" in kwargs_dict:
                    has_report_id = True
            except Exception:
                pass

            if not has_report_id:
                warnings.append(
                    Warning(
                        f"PeriodicTask '{task.name}' targets 'refresh_report' but is missing the required 'report_id' argument. "
                        "Did you mean to use 'reports_refresh' instead?",
                        obj=task,
                        id="power_query.W001",
                    )
                )
    except (OperationalError, ProgrammingError):
        pass
    return warnings
