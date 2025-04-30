import pytest
from unittest import mock

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.storage import default_storage
from django.urls import reverse

from hope_country_report.apps.power_query.models import Dataset, Query


@pytest.fixture()
def query():
    from testutils.factories import ContentTypeFactory, QueryFactory

    return QueryFactory(
        target=ContentTypeFactory(app_label="auth", model="permission"), name="Query", code="result=conn.all()"
    )


@pytest.fixture()
def dataset():
    from testutils.factories import DatasetFactory

    return DatasetFactory()


def test_celery_terminate(django_app, admin_user, query):
    """Test the celery terminate action for Query."""
    url = reverse("admin:power_query_query_celery_terminate", args=[query.pk])

    change_url = reverse("admin:power_query_query_change", args=[query.pk])

    with mock.patch.object(Query, "is_queued", return_value=False):
        res_get = django_app.get(url, user=admin_user, headers={"Referer": change_url})
        assert res_get.status_code == 302
        assert res_get.location == change_url
        res_follow = res_get.follow(expect_errors=True)
        messages = [m.message for m in res_follow.context["messages"]]
        assert "Task not queued." in messages

    with mock.patch.object(Query, "is_queued", return_value=True):
        with mock.patch.object(Query, "terminate") as mock_terminate:
            res = django_app.get(url, user=admin_user, headers={"Referer": change_url})
            assert res.status_code == 200
            assert "Confirm termination request" in res.text
            assert str(query) in res.text

            change_url = reverse("admin:power_query_query_change", args=[query.pk])

            res_post = res.forms[1].submit()
            assert res_post.status_code == 302
            assert res_post.location == change_url, "Redirect should go back to the change page"
            mock_terminate.assert_called_once()

            res_follow = res_post.follow()
            messages = [m.message for m in res_follow.context["messages"]]
            assert len(messages) > 0, "Expected success/info message after terminate"


def test_celery_inspect(django_app, admin_user, query):
    """Test the celery inspect view for Query."""
    url = reverse("admin:power_query_query_celery_inspect", args=[query.pk])
    with mock.patch.object(Query, "curr_async_result_id", "some-task-id", create=True):
        res = django_app.get(url, user=admin_user)
        assert res.status_code == 200


def test_celery_queue(django_app, admin_user, query):
    """Test the celery queue action for Query."""
    url = reverse("admin:power_query_query_celery_queue", args=[query.pk])

    with mock.patch.object(Query, "queue") as mock_queue:
        res = django_app.get(url, user=admin_user, headers={"Referer": url})
        assert res.status_code == 200
        assert f"Confirm queue action for {query}" in res.text

        res_post = res.forms[1].submit()
        assert res_post.status_code == 302
        expected_redirect_url = reverse("admin:power_query_query_change", args=[query.pk])
        assert res_post.location == expected_redirect_url
        mock_queue.assert_called_once()

    res_follow = res_post.follow()
    assert res_follow.status_code == 200
    messages = [m.message for m in res_follow.context["messages"]]
    assert "Queued" in messages

    change_url = reverse("admin:power_query_query_change", args=[query.pk])
    with mock.patch.object(Query, "is_queued", return_value=True):
        res_get_already_queued = django_app.get(url, user=admin_user, headers={"Referer": change_url})
        assert res_get_already_queued.status_code == 302
        assert res_get_already_queued.location == change_url
        res_follow_already_queued = res_get_already_queued.follow(expect_errors=True)
        messages = [m.message for m in res_follow_already_queued.context["messages"]]
        assert "Task has already been queued." in messages


def test_celery_revoke(django_app, admin_user, query):
    """Test the celery revoke action for Query."""
    url = reverse("admin:power_query_query_celery_revoke", args=[query.pk])

    change_url = reverse("admin:power_query_query_change", args=[query.pk])

    with mock.patch.object(Query, "is_queued", return_value=False):
        res_get_not_queued = django_app.get(url, user=admin_user, headers={"Referer": change_url})
        assert res_get_not_queued.status_code == 302
        assert res_get_not_queued.location == change_url
        res_follow_not_queued = res_get_not_queued.follow(expect_errors=True)
        messages = [m.message for m in res_follow_not_queued.context["messages"]]
        assert "Task not queued." in messages

    with mock.patch.object(Query, "is_queued", return_value=True):
        with mock.patch.object(Query, "revoke") as mock_revoke:
            res = django_app.get(url, user=admin_user, headers={"Referer": change_url})
            assert res.status_code == 200
            assert "Confirm revoking action for [ABSTRACT]" in res.text
            assert str(query) in res.text

            res_post = res.forms[1].submit()
            assert res_post.status_code == 302

            change_url = reverse("admin:power_query_query_change", args=[query.pk])
            assert res_post.location == change_url, "Redirect should go back to the change page"
            mock_revoke.assert_called_once()

            res_follow = res_post.follow()
            messages = [m.message for m in res_follow.context["messages"]]
            assert "Revoked" in messages


def test_query_run(django_app, admin_user, query):
    """Test the non-celery 'run' action (likely for debug/dev)."""
    url = reverse("admin:power_query_query_run", args=[query.pk])
    res = django_app.get(url, user=admin_user)
    res = django_app.get(url, user=admin_user)
    assert res.status_code == 200


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
