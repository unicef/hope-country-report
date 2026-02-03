import pytest
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from hope_country_report.apps.power_query.models import Dataset
from hope_country_report.state import state
from testutils.factories import (
    DatasetFactory,
    QueryFactory,
    ReportConfigurationFactory,
    ReportDocumentFactory,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def token(user):
    from rest_framework.authtoken.models import Token

    return Token.objects.create(user=user)


@pytest.fixture
def query(db, afghanistan, user):
    return QueryFactory(name="Test Query", country_office=afghanistan, owner=user, code="result = [{'id': 1}]")


@pytest.fixture
def authorized_user(afg_user, reporters):
    from django.contrib.auth.models import Permission

    perms = Permission.objects.filter(
        content_type__app_label="power_query",
        codename__in=["view_query", "view_dataset"],
    )
    reporters.permissions.add(*perms)
    return afg_user


@pytest.fixture
def dataset(db, query, afghanistan):
    import pickle
    from hope_country_report.state import state

    with state.set(tenant=afghanistan):
        data = [{"id": 1, "value": "test"}]

        return DatasetFactory(
            query=query,
            hash="test_hash",
            value=pickle.dumps(data),
        )


@pytest.fixture
def config(db, query, afghanistan):
    from hope_country_report.state import state

    with state.set(tenant=afghanistan):
        return ReportConfigurationFactory(
            name="test_report", title="Test Report", query=query, country_office=afghanistan
        )


@pytest.fixture
def formatter(db, afghanistan):
    from hope_country_report.state import state
    from testutils.factories import FormatterFactory

    with state.set(tenant=afghanistan):
        return FormatterFactory(name="JSON", file_suffix=".json", country_office=afghanistan)


@pytest.fixture
def document(db, config, dataset, afghanistan, formatter):
    from django.core.files.base import ContentFile
    from hope_country_report.state import state

    with state.set(tenant=afghanistan):
        return ReportDocumentFactory(
            title="Test Document",
            report=config,
            dataset=dataset,
            formatter=formatter,
            file=ContentFile(b"{}", name="test.json"),
        )


def test_authentication_required(api_client, afghanistan, query):
    url = reverse(
        "api:dataset-list",
        kwargs={"parent_lookup_query__country_office__slug": afghanistan.slug, "parent_lookup_query": query.pk},
    )
    response = api_client.get(url)
    assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]


def test_list_datasets(api_client, authorized_user, token, afghanistan, query, dataset):
    assert authorized_user.has_perm("power_query.view_dataset", dataset)
    assert Dataset.objects.filter(pk=dataset.pk).exists()

    api_client.credentials(HTTP_AUTHORIZATION="Token " + token.key)
    url = reverse(
        "api:dataset-list",
        kwargs={"parent_lookup_query__country_office__slug": afghanistan.slug, "parent_lookup_query": query.pk},
    )

    with state.set(tenant=afghanistan):
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK

        results = response.data.get("results", response.data) if isinstance(response.data, dict) else response.data
        assert len(results) == 1
        item = results[0]
        assert "hash" in item
        assert "data" not in item


def test_retrieve_dataset(api_client, authorized_user, token, afghanistan, query, dataset):
    api_client.credentials(HTTP_AUTHORIZATION="Token " + token.key)
    url = reverse(
        "api:dataset-detail",
        kwargs={
            "parent_lookup_query__country_office__slug": afghanistan.slug,
            "parent_lookup_query": query.pk,
            "pk": dataset.pk,
        },
    )

    with state.set(tenant=afghanistan):
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert "data" in response.data


def test_report_config_has_datasets_url(api_client, authorized_user, token, afghanistan, query, config):
    with state.set(tenant=afghanistan):
        api_client.credentials(HTTP_AUTHORIZATION="Token " + token.key)
        url = reverse(
            "api:config-detail", kwargs={"parent_lookup_country_office__slug": afghanistan.slug, "pk": config.pk}
        )

        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert "datasets_url" in response.data
        assert str(response.data["datasets_url"]).endswith(
            f"/api/offices/{afghanistan.slug}/queries/{query.pk}/dataset/"
        )


def test_document_has_dataset_url(api_client, authorized_user, token, afghanistan, query, document, dataset):
    with state.set(tenant=afghanistan):
        api_client.credentials(HTTP_AUTHORIZATION="Token " + token.key)
        url = reverse(
            "api:document-detail",
            kwargs={
                "parent_lookup_report__country_office__slug": afghanistan.slug,
                "parent_lookup_report__id": document.report.pk,
                "pk": document.pk,
            },
        )

        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert "dataset_url" in response.data
        assert str(response.data["dataset_url"]).endswith(
            f"/api/offices/{afghanistan.slug}/queries/{query.pk}/dataset/{dataset.pk}/"
        )
