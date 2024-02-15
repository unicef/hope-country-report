from typing import TYPE_CHECKING

import pytest

from django.core.exceptions import ValidationError

if TYPE_CHECKING:
    from hope_country_report.apps.power_query.models import Parametrizer


@pytest.fixture()
def query(db):
    from testutils.factories import ContentTypeFactory, QueryFactory

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
