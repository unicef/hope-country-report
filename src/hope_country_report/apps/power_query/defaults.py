from typing import TYPE_CHECKING

from django.contrib.auth import get_user_model

if TYPE_CHECKING:
    from typing import Any, Dict, List

    from hope_country_report.apps.power_query.models import Formatter


def create_defaults() -> "List[Formatter]":
    if get_user_model().objects.filter(is_superuser=True).first() is None:
        return []
    from django.contrib.contenttypes.models import ContentType

    from hope_country_report.apps.hope.models import Program
    from hope_country_report.apps.power_query.models import Formatter, Parametrizer, Query, Report

    SYSTEM_PARAMETRIZER: Dict[str, Dict[str, Any]] = {
        "active-programs": {
            "name": "Active Programs",
            "value": lambda: {"partner": list(Program.objects.filter(status="ACTIVE").values_list("name", flat=True))},
        },
    }

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
"""
        },
    )

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
            "content_type": "html",
        },
    )

    f2, __ = Formatter.objects.get_or_create(name="Dataset To XLS", defaults={"code": "", "content_type": "xls"})

    for code, params in SYSTEM_PARAMETRIZER.items():
        Parametrizer.objects.update_or_create(
            name=params["name"], code=code, defaults={"system": True, "value": params["value"]()}
        )
    q, __ = Query.objects.get_or_create(
        name="Households for Program",
        target=ContentType.objects.get(app_label="hope", model="household"),
        parametrizer__code="active-programs",
        code="result=conn.filter()",
    )
    Report.objects.update_or_create(
        name="Household by BusinessArea",
        defaults={"query": q, "formatter": f2, "title": "Household by BusinessArea: %(business_area)s"},
    )

    return [f1, f2]
