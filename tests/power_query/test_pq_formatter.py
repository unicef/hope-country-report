from typing import TYPE_CHECKING

import pytest

from strategy_field.utils import fqn

from hope_country_report.apps.power_query import processors
from hope_country_report.state import state

if TYPE_CHECKING:
    from hope_country_report.apps.core.models import CountryOffice, User
    from hope_country_report.apps.power_query.models import Formatter, Query


@pytest.fixture()
def data(user: "User"):
    from testutils.factories import CountryOfficeFactory, HouseholdFactory

    with state.set(must_tenant=False):
        co1: "CountryOffice" = CountryOfficeFactory(name="Afghanistan")

        HouseholdFactory(id="hh_id1", business_area=co1.business_area, withdrawn=False)
        HouseholdFactory(id="hh_id2", business_area=co1.business_area, withdrawn=False)
        HouseholdFactory(id="hh_id3", business_area=co1.business_area, withdrawn=False)


@pytest.fixture()
def query1(data):
    from testutils.factories import ContentTypeFactory, QueryFactory

    return QueryFactory(
        target=ContentTypeFactory(app_label="hope", model="household"),
        name="Query1",
        code="result=conn.order_by('id')",
    )


@pytest.fixture()
def dataset(query1: "Query"):
    query1.run(persist=True)
    return query1.datasets.first()


def test_formatter_html_detail(dataset):
    from testutils.factories import FormatterFactory

    fmt: "Formatter" = FormatterFactory(
        name="f1",
        code="<html><body>{{page}}</body></html>",
        processor=fqn(processors.ToHTML),
        type=processors.TYPE_DETAIL,
        file_suffix=".html",
    )
    result = fmt.render({"dataset": dataset})
    content = result.decode()
    assert content == "<html><body>1</body></html><html><body>2</body></html><html><body>3</body></html>"


def test_formatter_html_list(dataset):
    from testutils.factories import FormatterFactory

    fmt: "Formatter" = FormatterFactory(
        name="f1",
        code="<html><body>{% for record in dataset.data %}<div>{{record.id}}</div>{% endfor %}</body></html>",
        processor=fqn(processors.ToHTML),
        type=processors.TYPE_LIST,
    )
    result = fmt.render({"dataset": dataset})
    content = result.decode()
    assert content == "<html><body><div>hh_id1</div><div>hh_id2</div><div>hh_id3</div></body></html>"


def test_formatter_htmlpdf_list(dataset):
    from testutils.factories import FormatterFactory

    fmt: "Formatter" = FormatterFactory(
        name="f1",
        code="<html><body>{% for record in dataset.data %}<div>{{record.id}}</div>{% endfor %}</body></html>",
        processor=fqn(processors.ToHTML),
        type=processors.TYPE_LIST,
    )
    result = fmt.render({"dataset": dataset})
    content = result.decode()
    assert content == "<html><body><div>hh_id1</div><div>hh_id2</div><div>hh_id3</div></body></html>"
