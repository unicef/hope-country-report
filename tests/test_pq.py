import pytest

from hope_country_report.state import state


@pytest.fixture()
def country_office(office):
    return office


@pytest.fixture()
def tenant_user(country_office):
    from testutils.factories import UserFactory, UserRoleFactory

    u = UserFactory()
    UserRoleFactory()
    return u


def test_filter_query(tenant_user):
    from testutils.factories import QueryFactory

    q = QueryFactory()

    with state.set():
        q.run()
