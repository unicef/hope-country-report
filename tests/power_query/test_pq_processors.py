from typing import TYPE_CHECKING

import pickle

import pytest
from unittest.mock import Mock

from docxtpl import DocxTemplate
from pypdf import PdfReader
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


def test_processor_html(dataset, tmp_path):
    from testutils.factories import FormatterFactory

    fmt = FormatterFactory(name="Queryset To HTML")
    assert processors.ToHTML(fmt).process({"dataset": dataset})


def test_processor_xls(dataset, tmp_path):
    result = processors.ToXLS(Mock()).process({"dataset": dataset})
    # Path("AAAA.xls").write_bytes(result)
    assert result


def test_processor_yml(dataset, tmp_path):
    result = processors.ToYAML(Mock()).process({"dataset": dataset})
    # Path("AAAA.yml").write_text(result)
    assert result


def test_processor_json(dataset, tmp_path):
    result = processors.ToJSON(Mock()).process({"dataset": dataset})
    # Path("AAAA.json").write_text(result)
    assert result


def test_processor_docx(dataset, tmp_path):
    from testutils.factories import ReportTemplateFactory

    tpl = ReportTemplateFactory(name="households.docx")

    fmt = Mock()
    fmt.template = tpl

    result = processors.ToWord(fmt).process({"dataset": dataset, "business_area": "Afghanistan", "project": ""})
    # try ti save and open
    output = tmp_path / "AAAA.docx"
    output.write_bytes(result.read())
    DocxTemplate(output)
    assert result


def test_processor_pdf(dataset, tmp_path):
    from testutils.factories import FormatterFactory

    code = FormatterFactory(name="Queryset To HTML").code
    fmt = FormatterFactory(name="aaa", code=code)

    result = processors.ToPDF(fmt).process({"dataset": dataset, "business_area": "Afghanistan"})
    output = tmp_path / "AAAA.pdf"
    output.write_bytes(result)
    PdfReader(output)
    assert result


def test_processor_pdfform(dataset, tmp_path):
    from testutils.factories import ReportTemplateFactory

    tpl = ReportTemplateFactory(name="program_receipt.pdf")

    fmt = Mock()
    fmt.template = tpl
    result = processors.ToFormPDF(fmt).process({"dataset": dataset, "business_area": "Afghanistan"})
    # try ti save and open
    output = tmp_path / "AAAA.pdf"
    output.write_bytes(result.read())
    PdfReader(output)
    assert result
