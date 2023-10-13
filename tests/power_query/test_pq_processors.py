from typing import TYPE_CHECKING

import pickle

import pytest
from unittest.mock import Mock

from testutils.factories import DatasetFactory

from hope_country_report.apps.power_query import processors
from hope_country_report.state import state

if TYPE_CHECKING:
    from hope_country_report.apps.core.models import CountryOffice


@pytest.fixture()
def data(user):
    from testutils.factories import CountryOfficeFactory, HouseholdFactory

    with state.set(must_tenant=False):
        co1: "CountryOffice" = CountryOfficeFactory(name="Afghanistan")

        HouseholdFactory(business_area=co1.business_area, withdrawn=False)
        HouseholdFactory(business_area=co1.business_area, withdrawn=False)
        HouseholdFactory(business_area=co1.business_area, withdrawn=False)


@pytest.fixture()
def query1(data):
    from testutils.factories import ContentTypeFactory, QueryFactory

    return QueryFactory(
        target=ContentTypeFactory(app_label="hope", model="household"),
        name="Query1",
        code="result=conn.all()",
    )


@pytest.fixture()
def formatter():
    from testutils.factories import FormatterFactory

    return FormatterFactory(name="Queryset To HTML")


@pytest.fixture()
def report(query1, formatter):
    from testutils.factories import ReportFactory

    return ReportFactory(formatter=formatter, query=query1)


@pytest.fixture
def dataset(data, report):
    from hope_country_report.apps.hope.models import Household

    return DatasetFactory(value=pickle.dumps(Household.objects.all()))


def test_processor_html(dataset):
    from testutils.factories import FormatterFactory

    fmt = FormatterFactory(name="Queryset To HTML")
    assert processors.ToHTML(fmt).process({"dataset": dataset})


def test_processor_xls(dataset):
    result = processors.ToXLS(Mock()).process({"dataset": dataset})
    # Path("AAAA.xls").write_bytes(result)
    assert result


def test_processor_yml(dataset):
    result = processors.ToYAML(Mock()).process({"dataset": dataset})
    # Path("AAAA.yml").write_text(result)
    assert result


def test_processor_json(dataset):
    result = processors.ToJSON(Mock()).process({"dataset": dataset})
    # Path("AAAA.json").write_text(result)
    assert result


def test_processor_docx(dataset):
    from testutils.factories import ReportTemplateFactory

    tpl = ReportTemplateFactory(name="households.docx")

    fmt = Mock()
    fmt.template = tpl

    result = processors.ToWord(fmt).process({"dataset": dataset, "business_area": "Afghanistan"})
    # Path("AAAA.docx").write_bytes(result)
    assert result
