import pytest

from django.urls import reverse


@pytest.fixture()
def query():
    from testutils.factories import ContentTypeFactory, QueryFactory

    return QueryFactory(
        target=ContentTypeFactory(app_label="auth", model="permission"),
        name="Query1",
        code="result=conn.all()",
    )


def test_celery_discard_all(request, django_app, admin_user):
    url = reverse("admin:power_query_query_celery_discard_all")
    res = django_app.get(url, user=admin_user)
    assert res.status_code == 302


def test_celery_purge(request, django_app, admin_user):
    url = reverse("admin:power_query_query_celery_purge")
    res = django_app.get(url, user=admin_user)
    assert res.status_code == 302


def test_celery_terminate(request, django_app, admin_user, query):
    url = reverse("admin:power_query_query_celery_terminate", args=[query.pk])
    res = django_app.get(url, user=admin_user)
    assert res.status_code == 302


def test_celery_inspect(request, django_app, admin_user, query):
    url = reverse("admin:power_query_query_celery_inspect", args=[query.pk])
    query.queue()
    res = django_app.get(url, user=admin_user)
    assert res.status_code == 200


def test_celery_result(request, django_app, admin_user, query):
    url = reverse("admin:power_query_query_celery_result", args=[query.pk])
    query.queue()
    res = django_app.get(url, user=admin_user)
    assert res.status_code == 302


def test_celery_queue(request, django_app, admin_user, query):
    url = reverse("admin:power_query_query_celery_queue", args=[query.pk])
    res = django_app.get(url, user=admin_user)
    assert res.status_code == 302


def test_check_status(request, django_app, admin_user, query):
    url = reverse("admin:power_query_query_check_status")
    res = django_app.get(url, user=admin_user)
    assert res.status_code == 302
