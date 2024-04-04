from typing import TYPE_CHECKING

import pytest

from django.core.exceptions import ValidationError

from testutils.factories import ContentTypeFactory, CountryOfficeFactory, ParametrizerFactory, QueryFactory

if TYPE_CHECKING:
    from hope_country_report.apps.power_query.models import Parametrizer


@pytest.fixture()
def query(db):
    q1 = QueryFactory(
        name="q1",
        target=ContentTypeFactory(app_label="auth", model="permission"),
        code="result=conn.filter(codename__startswith='change_group').values_list('codename', flat=True)",
    )
    q1.run(True)
    return q1


def test_str() -> None:
    # admin choices should display name
    from testutils.factories import ParametrizerFactory

    p: "Parametrizer" = ParametrizerFactory()
    assert str(p) == p.name


def test_parameter_clean() -> None:
    from testutils.factories import ParametrizerFactory

    p: "Parametrizer" = ParametrizerFactory.build(source=None, value=2)
    with pytest.raises(ValidationError):
        p.clean()
    p: "Parametrizer" = ParametrizerFactory.build(source=None, value=[1, 2, 3])
    assert p.clean()

    p: "Parametrizer" = ParametrizerFactory.build(source=None, value={"day": [1, 2, 3]})
    assert p.clean()


def test_parameter_query(query) -> None:
    from testutils.factories import ParametrizerFactory

    p: "Parametrizer" = ParametrizerFactory(source=query)
    p.refresh()
    assert p.value == ["change_group", "change_groupresult"]

    p.source = None  # refresh without source should not raise error
    p.refresh()
    assert p


def test_parameter_fixed_dict() -> None:
    from testutils.factories import ParametrizerFactory

    p: "Parametrizer" = ParametrizerFactory(name="Days", source=None, value={"day": [1, 2, 3]})
    assert p.get_matrix() == [{"day": 1}, {"day": 2}, {"day": 3}]


def test_parameter_fixed_list() -> None:
    from testutils.factories import ParametrizerFactory

    p: "Parametrizer" = ParametrizerFactory(name="Days", code="", source=None, value=[1, 2, 3])
    assert p.get_matrix() == [{"days": 1}, {"days": 2}, {"days": 3}]


@pytest.fixture
def parent_query_with_parametrizer(db):
    """
    Create a parent query with a Parametrizer
    """
    parametrizer = ParametrizerFactory(value={"withdrawn": [True, False]}, name="p1")
    parent_query = QueryFactory(
        name="parent_query",
        parametrizer=parametrizer,
        target=ContentTypeFactory(app_label="auth", model="permission"),
        code="result=conn.all()",
    )
    parent_query.run(True)
    return parent_query


@pytest.fixture
def child_query_no_parametrizer(db, parent_query_with_parametrizer):
    """
    Create a child query without its own Parametrizer, linked to a parent query
    """
    child_query = QueryFactory(
        name="child_query",
        country_office=CountryOfficeFactory(name="Afghanistan"),
        parent=parent_query_with_parametrizer,
        code=None,
        target=None,
    )
    child_query.run(True)
    return child_query


@pytest.fixture
def child_query_with_parametrizer(db, parent_query_with_parametrizer):
    """
    Create a child query with its own Parametrizer, linked to a parent query
    """
    parametrizer = ParametrizerFactory(value={"arg1": [1, 2], "arg2": [3, 4]}, name="p2")
    child_query = QueryFactory(
        name="child_query_own_parametrizer",
        country_office=CountryOfficeFactory(name="Afghanistan"),
        parent=parent_query_with_parametrizer,
        parametrizer=parametrizer,
        code=None,
        target=None,
    )
    child_query.run(True)
    return child_query


def test_get_args_inherits_from_parent(child_query_no_parametrizer):
    args = child_query_no_parametrizer.get_args()
    assert args == [{"withdrawn": True}, {"withdrawn": False}], "Should inherit args from parent"


def test_get_args_uses_own_parametrizer(child_query_with_parametrizer):
    args = child_query_with_parametrizer.get_args()
    assert args == [
        {"arg1": 1, "arg2": 3},
        {"arg1": 1, "arg2": 4},
        {"arg1": 2, "arg2": 3},
        {"arg1": 2, "arg2": 4},
    ], "Should use its own parametrizer"


def test_get_args_default_behavior(query):
    """
    Assuming `query` is a fixture for a query without a parametrizer and without a parent
    """
    args = query.get_args()
    assert args == [{}], "Should return default args when no parametrizer is set"
