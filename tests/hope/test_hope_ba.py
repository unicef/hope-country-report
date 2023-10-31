import pytest

from hope_country_report.state import state


@pytest.fixture
def data():
    from testutils.factories import CountryOfficeFactory

    return [CountryOfficeFactory(name="Afghanistan"), CountryOfficeFactory(name="Niger")]


def test_ba_manager(data):
    from hope_country_report.apps.hope.models import BusinessArea

    assert BusinessArea.objects.count() == 2
    with state.set(must_tenant=True, tenant=data[0]):
        assert BusinessArea.objects.count() == 1
