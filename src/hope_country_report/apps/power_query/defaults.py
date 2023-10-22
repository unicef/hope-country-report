from typing import TYPE_CHECKING

from strategy_field.utils import fqn

from hope_country_report.apps.power_query.processors import ToHTML, ToXLS

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
            "content_type": ".html",
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
            "content_type": ".html",
        },
    )
    q1, __ = Query.objects.get_or_create(
        name="Active Programs",
        defaults={
            "target": ContentType.objects.get(app_label="hope", model="program"),
            "code": "result=conn.filter(status='ACTIVE').values_list('name', flat=True)",
        },
    )
    q1.run(True)
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
    r1.formatters.add(f2)
    f3, __ = Formatter.objects.get_or_create(name="Dataset To XLS", defaults={"code": "", "processor": fqn(ToXLS)})

    ReportTemplate.load()

    return [f1, f2, f3]
