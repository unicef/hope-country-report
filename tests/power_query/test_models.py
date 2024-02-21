from typing import TYPE_CHECKING

import pytest

from django.db import IntegrityError

from extras.testutils.factories import ContentTypeFactory, QueryFactory

if TYPE_CHECKING:
    from hope_country_report.apps.power_query.models import Query


@pytest.fixture()
def query():
    from testutils.factories import ContentTypeFactory, QueryFactory

    return QueryFactory(
        target=ContentTypeFactory(app_label="hope", model="household"),
        name="Query *",
        code="result=conn.all()",
    )


def test_query_valid_abstract():
    query = QueryFactory(
        target=ContentTypeFactory(app_label="auth", model="permission"),
        name="Query",
        code="result=conn.all()",
        parent=None,
    )
    assert str(query) == "[ABSTRACT] Query"


def test_query_valid_query_implementation(query: "Query"):
    query = QueryFactory(
        target=None,
        name="Query",
        code=None,
        parent=query,
    )
    assert str(query) == "Query (Query *)"


# def test_query_invalid_query_parent_without_code():
#     with pytest.raises(IntegrityError):
#         QueryFactory(
#             target=ContentTypeFactory(app_label="auth", model="permission"),
#             name="Query",
#             code=None,
#             parent=None,
#             country_office=None,
#         )
#
#
# def test_query_invalid_query_implementation_with_target(query: "Query"):
#     with pytest.raises(IntegrityError):
#         QueryFactory(
#             target=ContentTypeFactory(app_label="auth", model="permission"),
#             name="Query",
#             code=None,
#             parent=query,
#             country_office=None,
#         )
#
#
# def test_query_invalid_query_implementation_with_code(query: "Query"):
#     with pytest.raises(IntegrityError):
#         QueryFactory(
#             target=None,
#             name="Query",
#             code="result=conn.all()",
#             parent=query,
#             country_office=None,
#         )
