from typing import TYPE_CHECKING

from strategy_field.utils import fqn

from hope_country_report.apps.power_query.processors import ToCSV, ToHTML, ToJSON, ToPDF, ToText, ToXLS, ToXLSX, ToYAML

if TYPE_CHECKING:
    from hope_country_report.apps.power_query.models import Formatter


def create_defaults() -> "list[Formatter]":
    from hope_country_report.apps.power_query.models import Formatter, ReportTemplate

    Formatter.objects.get_or_create(
        name="Queryset To HTML",
        defaults={
            "code": """
<h1>{{title}}</h1>
<table>
    <tr><th>id</th><th>str</th></tr>
{% for row in dataset.data %}<tr>
    <td>{{ row.id }}</td>
    <td>{{ row }}</td>
    </tr>
{% endfor %}
    </table>
""",
            "processor": fqn(ToHTML),
            "file_suffix": ".html",
        },
    )

    Formatter.objects.get_or_create(
        name="Queryset To Text",
        defaults={
            "code": """
{% for row in dataset.data %}{{ row }}
{% endfor %}""",
            "processor": fqn(ToText),
            "file_suffix": ".txt",
        },
    )
    Formatter.objects.get_or_create(
        name="Code To PDF",
        defaults={
            "code": """
    {% for row in dataset.data %}{{ row }}
    {% endfor %}""",
            "processor": fqn(ToPDF),
            "file_suffix": ".pdf",
        },
    )

    for p in [ToYAML, ToJSON, ToXLS, ToCSV, ToXLSX]:
        Formatter.objects.get_or_create(
            name=p.verbose_name,
            defaults={
                "code": "",
                "processor": fqn(p),
                "file_suffix": p.file_suffix,
            },
        )

    ReportTemplate.load()

    return Formatter.objects.all()


def create_periodic_tasks():
    from django_celery_beat.models import CrontabSchedule, PeriodicTask

    import hope_country_report.apps.power_query.celery_tasks

    sunday, __ = CrontabSchedule.objects.get_or_create(day_of_week="0")
    first_of_month, __ = CrontabSchedule.objects.get_or_create(day_of_month="1")

    PeriodicTask.objects.get_or_create(
        name="Refresh every Sunday",
        defaults={
            "task": fqn(hope_country_report.apps.power_query.celery_tasks.reports_refresh),
            "crontab": sunday,
        },
    )

    PeriodicTask.objects.get_or_create(
        name="Refresh First Of Month",
        defaults={
            "task": fqn(hope_country_report.apps.power_query.celery_tasks.reports_refresh),
            "crontab": first_of_month,
        },
    )
