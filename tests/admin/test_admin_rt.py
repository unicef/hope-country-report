import pytest

from django.urls import reverse

from strategy_field.utils import fqn

from hope_country_report.apps.power_query.processors import ToHTML


@pytest.fixture
def report_template():
    from testutils.factories import ReportTemplateFactory

    return ReportTemplateFactory()


@pytest.fixture
def dataset():
    from testutils.factories import DatasetFactory

    return DatasetFactory()


def test_templeta_preview(report_template, dataset, django_app, admin_user):
    url = reverse("admin:power_query_reporttemplate_preview", args=[report_template.pk])
    res = django_app.get(url, user=admin_user)
    res.forms["template-form"]["dataset"] = dataset.pk
    res.forms["template-form"]["processor"] = fqn(ToHTML)

    res = res.forms["template-form"].submit()
    assert res.status_code == 200
