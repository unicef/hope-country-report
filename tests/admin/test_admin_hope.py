import pytest

from django.urls import reverse

from hope_country_report.apps.power_query.processors import TYPE_DETAIL


@pytest.fixture()
def query_qs():
    from testutils.factories import ContentTypeFactory, QueryFactory

    return QueryFactory(
        target=ContentTypeFactory(app_label="auth", model="permission"),
        name="Query1",
        code="result=conn.all()",
    )


@pytest.fixture()
def query_list():
    from testutils.factories import ContentTypeFactory, QueryFactory

    return QueryFactory(
        target=ContentTypeFactory(app_label="auth", model="permission"),
        name="Query1",
        code="result=list(conn.values())",
    )


@pytest.fixture()
def query_ds():
    from testutils.factories import ContentTypeFactory, QueryFactory

    return QueryFactory(
        target=ContentTypeFactory(app_label="auth", model="permission"),
        name="Query1",
        code="result=to_dataset(conn.all())",
    )


@pytest.fixture()
def formatter():
    from testutils.factories import ContentTypeFactory, FormatterFactory

    return FormatterFactory(
        target=ContentTypeFactory(app_label="auth", model="permission"),
        name="f1",
        code="result=to_dataset(conn.all())",
    )


@pytest.mark.parametrize("q", ["query_qs", "query_list", "query_ds"])
def test_query_preview(request, q, django_app, admin_user):
    query = request.getfixturevalue(q)
    url = reverse("admin:power_query_query_preview", args=[query.pk])
    res = django_app.get(url, user=admin_user)
    assert res.pyquery("#query-results")[0].tag == "table"


@pytest.mark.parametrize("q", ["query_qs", "query_list", "query_ds"])
def test_dataset_preview(request, q, django_app, admin_user):
    query = request.getfixturevalue(q)
    query.run(True)
    url = reverse("admin:power_query_dataset_preview", args=[query.datasets.first().pk])
    res = django_app.get(url, user=admin_user)
    assert res.pyquery("#query-results")[0].tag == "table"


@pytest.mark.parametrize("q", ["query_qs", "query_list", "query_ds"])
def test_formatter_test(request, q, django_app, admin_user):
    from testutils.factories import FormatterFactory

    fmt = FormatterFactory(name="f1", code="- {{record.pk}}\n", type=TYPE_DETAIL)
    query = request.getfixturevalue(q)
    query.run(True)
    url = reverse("admin:power_query_formatter_test", args=[fmt.pk])
    res = django_app.get(url, user=admin_user)
    res.forms["formatter-form"]["query"] = query.pk
    res = res.forms["formatter-form"].submit()
    assert res.pyquery("div.results")
