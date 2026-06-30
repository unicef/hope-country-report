import pytest
from rest_framework.test import APIClient

pytestmark = [pytest.mark.api, pytest.mark.django_db]


@pytest.fixture()
def anonymous_client():
    return APIClient()


@pytest.mark.parametrize(
    "url",
    [
        "/api/home/",
        "/api/home/topology/",
        "/api/home/boundaries/",
        "/api/home/offices/",
        "/api/offices/",
        "/api/queries/",
        "/api/charts/",
    ],
)
def test_api_endpoints_reject_anonymous(anonymous_client, url):
    res = anonymous_client.get(url)
    # DjangoModelPermissions / DjangoObjectPermissions require authentication,
    # yielding either 401 Unauthorized or 403 Forbidden.
    assert res.status_code in (401, 403)
