import pytest
from django.urls import reverse


@pytest.fixture()
def report_template():
    from testutils.factories import ReportTemplate

    return ReportTemplate.objects.first()


@pytest.fixture()
def dataset():
    from testutils.factories import DatasetFactory

    return DatasetFactory()


def test_formatter_test(report_template, dataset, django_app, admin_user):
    url = reverse("admin:power_query_formatter_test", args=[report_template.pk])
    res = django_app.get(url, user=admin_user)
    res.forms["formatter-form"]["dataset"] = dataset.pk
    res = res.forms["formatter-form"].submit()

    assert res.status_code == 200


# @pytest.mark.parametrize("q", ["query_qs", "query_list", "query_ds"])
# def test_formatter_test(request, q, django_app, admin_user):
#     from testutils.factories import FormatterFactory
#
#     fmt = FormatterFactory(name="f1", code="- {{record.pk}}\n", type=TYPE_DETAIL, processor=fqn(ToHTML))
#     query = request.getfixturevalue(q)
#     query.run(True)
#     url = reverse("admin:power_query_formatter_test", args=[fmt.pk])
#     res = django_app.get(url, user=admin_user)
#     res.forms["formatter-form"]["dataset"] = query.pk
#     res = res.forms["formatter-form"].submit()
#     assert res.pyquery("div.results")
