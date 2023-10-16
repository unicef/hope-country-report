from typing import TYPE_CHECKING

import pytest

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


def test_parameter_query(query) -> None:
    from testutils.factories import ParametrizerFactory

    p: "Parametrizer" = ParametrizerFactory(source=query)
    p.refresh()
    assert p.value == ["change_group", "change_groupresult"]
