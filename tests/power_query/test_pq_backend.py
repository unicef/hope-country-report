from collections import namedtuple
from typing import TYPE_CHECKING

import pytest
from django.apps import apps
from django.contrib.auth.models import AnonymousUser
from testutils.factories import UserFactory, get_factory_for_model
from testutils.perms import user_grant_permissions

from hope_country_report.apps.power_query.backends import PowerQueryBackend
from hope_country_report.apps.power_query.exceptions import RequestablePermissionDenied
from hope_country_report.state import state

if TYPE_CHECKING:
    from hope_country_report.apps.core.models import CountryOffice
    from hope_country_report.apps.power_query.models import Query, ReportDocument

_DATA = namedtuple("_DATA", "afg,ukr,query_afg,query_ukr")


def pytest_generate_tests(metafunc):
    if "power_query_model" in metafunc.fixturenames:
        models = list(apps.get_app_config("power_query").get_models())
        metafunc.parametrize("power_query_model", models)


@pytest.fixture()
def data() -> _DATA:
    from testutils.factories import CountryOfficeFactory, QueryFactory

    with state.set(must_tenant=False):
        co1: "CountryOffice" = CountryOfficeFactory(name="Afghanistan")
        co2: "CountryOffice" = CountryOfficeFactory(name="Ukraine")
        q1: Query = QueryFactory(country_office=co1, owner=UserFactory())
        q2: Query = QueryFactory(country_office=co2, owner=UserFactory())
    return _DATA(co1, co2, q1, q2)


@pytest.fixture()
def backend():
    return PowerQueryBackend()


@pytest.fixture()
def restricted_document():
    from testutils.factories import ReportDocumentFactory, UserFactory

    doc: "ReportDocument" = ReportDocumentFactory(report__owner=UserFactory(username="owner"))
    doc.report.limit_access_to.add(UserFactory(username="allowed"))
    return doc


def test_invalid_perm(backend, user):
    assert not backend.has_perm(user, "aaaa")


def test_be_get_all_permissions_no_role(backend, user, data):
    assert backend.get_all_permissions(user, data.query_afg) == set()


def test_be_get_all_permissions_role(backend, user, data):
    with user_grant_permissions(user, "power_query.view_reportdocument", data.afg):
        assert backend.get_all_permissions(user, data.query_afg) == {"power_query.view_reportdocument"}
        # test cache
        assert backend.get_all_permissions(user, data.query_afg) == {"power_query.view_reportdocument"}
        assert backend.get_all_permissions(user, data.query_ukr) == set()


def test_be_has_perm(backend, user, data):
    assert not backend.has_perm(user, "power_query.view_reportdocument", data.query_afg)
    with user_grant_permissions(user, "power_query.view_reportdocument", data.afg):
        assert backend.has_perm(user, "power_query.view_reportdocument", data.query_afg)
        assert not backend.has_perm(user, "power_query.view_reportdocument", data.query_ukr)


def test_be_limit_access_to(backend, user, restricted_document):
    allowed = restricted_document.report.limit_access_to.first()
    with pytest.raises(RequestablePermissionDenied):
        assert not backend.has_perm(user, "power_query.view_reportdocument", restricted_document)

    assert not backend.has_perm(allowed, "power_query.view_reportdocument", restricted_document)

    with user_grant_permissions(allowed, "power_query.view_reportdocument", restricted_document.country_office):
        assert backend.has_perm(allowed, "power_query.view_reportdocument", restricted_document)


def test_be_owner_has_perm(backend, data):
    assert backend.has_perm(data.query_afg.owner, "power_query.view_reportdocument", data.query_afg)


def test_be_anonymous(backend, data):
    assert not backend.has_perm(AnonymousUser(), "power_query.view_reportdocument", data.query_afg)


def test_be_model_contract(backend, user, data, power_query_model):
    factory = get_factory_for_model(power_query_model)
    assert backend.get_all_permissions(user, factory()) == set()
