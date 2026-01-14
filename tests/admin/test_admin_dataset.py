from typing import TYPE_CHECKING

import pytest
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.storage import default_storage
from django.urls import reverse

if TYPE_CHECKING:
    from hope_country_report.apps.power_query.models import Dataset


@pytest.fixture()
def dataset():
    from testutils.factories import DatasetFactory

    return DatasetFactory()


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


@pytest.mark.parametrize("q", ["query_qs", "query_list", "query_ds"])
def test_dataset_preview(request, q, django_app, admin_user):
    query = request.getfixturevalue(q)
    query.run(True)
    url = reverse("admin:power_query_dataset_preview", args=[query.datasets.first().pk])
    res = django_app.get(url, user=admin_user)
    assert res.pyquery("#query-results")[0].tag == "table"


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
