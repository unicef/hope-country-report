import pytest

from strategy_field.utils import fqn

from hope_country_report.apps.power_query.processors import ToHTML


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


@pytest.fixture()
def formatter():
    from testutils.factories import ContentTypeFactory, FormatterFactory

    return FormatterFactory(
        target=ContentTypeFactory(app_label="auth", model="permission"),
        name="f1",
        processor=fqn(ToHTML),
        code="result=to_dataset(conn.all())",
    )
