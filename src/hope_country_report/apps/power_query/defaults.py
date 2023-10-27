from typing import TYPE_CHECKING

from strategy_field.utils import fqn

from hope_country_report.apps.power_query.processors import ToCSV, ToHTML, ToJSON, ToPDF, ToText, ToXLS, ToXLSX, ToYAML

if TYPE_CHECKING:
    from typing import List

    from hope_country_report.apps.power_query.models import Formatter


def create_defaults() -> "List[Formatter]":
    # if get_user_model().objects.filter(is_superuser=True).first() is None:
    #     return []
    from django.contrib.contenttypes.models import ContentType

    from hope_country_report.apps.power_query.models import Formatter, Parametrizer, Query, Report, ReportTemplate

    f1, __ = Formatter.objects.get_or_create(
        name="Dataset To HTML",
        defaults={
            "code": """
<h1>{{title}}</h1>
<table>
    <tr>{% for fname in dataset.data.headers %}<th>{{ fname }}</th>{% endfor %}</tr>
{% for row in dataset.data %}<tr>{% for col in row %}<td>{{ col }}</td>{% endfor %}</tr>
{% endfor %}
    </table>
""",
            "processor": fqn(ToHTML),
            "file_suffix": ".html",
        },
    )

    f2, __ = Formatter.objects.get_or_create(
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

    f2, __ = Formatter.objects.get_or_create(
        name="Queryset To Text",
        defaults={
            "code": """
{% for row in dataset.data %}{{ row }}
{% endfor %}""",
            "processor": fqn(ToText),
            "file_suffix": ".txt",
        },
    )
    f3, __ = Formatter.objects.get_or_create(
        name="Code To PDF",
        defaults={
            "code": """
    {% for row in dataset.data %}{{ row }}
    {% endfor %}""",
            "processor": fqn(ToPDF),
            "file_suffix": ".pdf",
        },
    )
    fmts = [f1, f2, f3]

    for p in [ToYAML, ToJSON, ToXLS, ToCSV, ToXLSX]:
        f, __ = Formatter.objects.get_or_create(
            name=p.verbose_name,
            defaults={
                "code": "",
                "processor": fqn(p),
                "file_suffix": p.file_suffix,
            },
        )
        fmts.append(f)

    #
    # f3, __ = Formatter.objects.get_or_create(name="Dataset To XLS", defaults={"code": "", "processor": fqn(ToXLS)})
    # Formatter.objects.get_or_create(name="Dataset To YAML", processor=fqn(ToYAML), content_type=ToYAML.content_type)
    # Formatter.objects.get_or_create(name="Dataset To JSON", processor=fqn(ToJSON), content_type=ToJSON.content_type)

    q1, __ = Query.objects.get_or_create(
        name="Active Programs",
        defaults={
            "target": ContentType.objects.get(app_label="hope", model="program"),
            "code": "result=conn.filter(status='ACTIVE').values_list('name', flat=True)",
        },
    )
    ds, __ = q1.run(True, use_existing=False)
    assert ds.file
    p1, __ = Parametrizer.objects.get_or_create(
        code="active-programs", defaults={"name": "Active Programs", "source": q1, "system": True}
    )
    p1.refresh()

    q2, __ = Query.objects.get_or_create(
        name="Households for Program",
        target=ContentType.objects.get(app_label="hope", model="household"),
        parametrizer=None,
        code="result=conn.filter()",
    )

    r1, __ = Report.objects.get_or_create(
        name="Household by Program",
        defaults={"query": q2, "title": "Household by BusinessArea: {program}"},
    )
    r1.formatters.add(*fmts)

    ReportTemplate.load()

    return fmts


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
