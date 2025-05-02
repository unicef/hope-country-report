import pytest

from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

from hope_country_report.apps.power_query.models import Query


@pytest.fixture()
def query():
    from testutils.factories import ContentTypeFactory, QueryFactory

    return QueryFactory(
        target=ContentTypeFactory(app_label="auth", model="permission"),
        name="Query1",
        code="result=conn.all()",
    )


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
def query_none():
    from testutils.factories import ContentTypeFactory, QueryFactory

    return QueryFactory(
        target=ContentTypeFactory(app_label="auth", model="permission"),
        name="Query1",
        code="result=None",
    )


@pytest.fixture()
def query_exception():
    from testutils.factories import ContentTypeFactory, QueryFactory

    return QueryFactory(
        target=ContentTypeFactory(app_label="auth", model="permission"),
        name="Query1",
        code="1/0",
    )


@pytest.fixture()
def dataset():
    from testutils.factories import DatasetFactory

    return DatasetFactory()


def test_query_run(request, django_app, admin_user, query):
    """Test the non-celery 'run' action."""
    url = reverse("admin:power_query_query_run", args=[query.pk])
    res = django_app.get(url, user=admin_user)
    assert res.status_code == 200


@pytest.mark.django_db()
def test_query_explain(django_app, admin_user, query: "Query"):
    url = reverse("admin:power_query_query_explain", args=[query.pk])
    res = django_app.get(url, user=admin_user)

    res = res.forms["explain-form"].submit()
    assert res.context["form"].errors

    res.forms["explain-form"]["target"] = ContentType.objects.get(app_label="hope", model="household").pk
    res = res.forms["explain-form"].submit()
    assert "sql" in res.context


@pytest.mark.parametrize("q", ["query_qs", "query_list", "query_ds"])
def test_query_preview(request, q, django_app, admin_user):
    query = request.getfixturevalue(q)
    url = reverse("admin:power_query_query_preview", args=[query.pk])
    res = django_app.get(url, user=admin_user)
    assert res.status_code == 200
    assert res.pyquery("#query-results")[0].tag == "table"


def test_query_preview_none(query_none, django_app, admin_user):
    url = reverse("admin:power_query_query_preview", args=[query_none.pk])
    res = django_app.get(url, user=admin_user)
    assert (
        res.pyquery("ul.messagelist .warning")[0].text
        == "Query does not returns a valid result. It returned <class 'NoneType'>"
    )


def test_query_preview_exception(query_exception, django_app, admin_user):
    preview_url = reverse("admin:power_query_query_preview", args=[query_exception.pk])
    res = django_app.get(preview_url, user=admin_user)
    assert res.status_code == 302
    assert res.location == "/"
    res_follow1 = res.follow()
    assert res_follow1.status_code == 302
    assert "/select-tenant/" in res_follow1.location
    res_follow2 = res_follow1.follow()
    assert res_follow2.status_code == 200
