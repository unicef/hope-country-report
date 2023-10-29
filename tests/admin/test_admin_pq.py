import pytest

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.storage import default_storage
from django.urls import reverse

from hope_country_report.apps.power_query.models import Dataset, Query


@pytest.fixture()
def query():
    from testutils.factories import ContentTypeFactory, QueryFactory

    return QueryFactory(
        target=ContentTypeFactory(app_label="auth", model="permission"),
        name="Query1",
        code="result=conn.all()",
    )


@pytest.fixture()
def dataset():
    from testutils.factories import DatasetFactory

    return DatasetFactory()


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


def test_celery_run(request, django_app, admin_user, query):
    url = reverse("admin:power_query_query_run", args=[query.pk])
    res = django_app.get(url, user=admin_user)
    assert res.status_code == 200


def test_check_status(request, django_app, admin_user, query):
    url = reverse("admin:power_query_query_check_status")
    res = django_app.get(url, user=admin_user)
    assert res.status_code == 302


@pytest.mark.django_db(transaction=True)
def test_delete_file(django_app, admin_user, dataset: "Dataset"):
    file_path = dataset.file.path
    assert default_storage.exists(file_path)
    url = reverse("admin:power_query_dataset_change", args=[dataset.pk])
    res = django_app.get(url, user=admin_user)
    res = res.click("Delete")
    res.forms[1].submit()
    with pytest.raises(ObjectDoesNotExist):
        dataset.refresh_from_db()
    assert not default_storage.exists(file_path)


@pytest.mark.django_db()
def test_query_explain(django_app, admin_user, query: "Query"):
    url = reverse("admin:power_query_query_explain", args=[query.pk])
    res = django_app.get(url, user=admin_user)

    res = res.forms["explain-form"].submit()
    assert res.context["form"].errors

    res.forms["explain-form"]["target"] = ContentType.objects.get(app_label="hope", model="household").pk
    res = res.forms["explain-form"].submit()
    assert "sql" in res.context
