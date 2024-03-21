from typing import TYPE_CHECKING

import uuid

import pytest
from unittest.mock import patch

from django.urls import reverse

from strategy_field.utils import fqn

from hope_country_report.apps.power_query import processors
from hope_country_report.apps.power_query.utils import get_image_url
from hope_country_report.state import state

if TYPE_CHECKING:
    from hope_country_report.apps.core.models import CountryOffice, User
    from hope_country_report.apps.power_query.models import Formatter, Query

H1, H2, H3 = sorted([uuid.uuid4(), uuid.uuid4(), uuid.uuid4()])


@pytest.fixture()
def data(user: "User"):
    from testutils.factories import CountryOfficeFactory, HouseholdFactory

    with state.set(must_tenant=False):
        co1: "CountryOffice" = CountryOfficeFactory(name="Afghanistan")

        HouseholdFactory(id=H1, business_area=co1.business_area, withdrawn=False)
        HouseholdFactory(id=H2, business_area=co1.business_area, withdrawn=False)
        HouseholdFactory(id=H3, business_area=co1.business_area, withdrawn=False)


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
        template=None,
        processor=fqn(processors.ToHTML),
        type=processors.TYPE_DETAIL,
        file_suffix=".html",
    )
    result = fmt.render({"dataset": dataset})
    content = result.decode()
    assert content == "<html><body>1</body></html><html><body>2</body></html><html><body>3</body></html>"


def test_formatter_html_multiple(dataset):
    from testutils.factories import FormatterFactory

    fmt: "Formatter" = FormatterFactory(
        name="f1",
        code="<html><body><div>{{records.0.id}}</div><div>{{records.1.id}}</div></body></html>",
        template=None,
        processor=fqn(processors.ToHTML),
        type=processors.TYPE_DETAIL,
        file_suffix=".html",
        item_per_page=2,
    )
    result = fmt.render({"dataset": dataset})
    content = result.decode()
    template = (
        f"<html><body><div>{H1}</div><div>{H2}</div></body></html>"
        f"<html><body><div>{H3}</div><div></div></body></html>"
    )
    assert content == template


def test_formatter_html_list(dataset):
    from testutils.factories import FormatterFactory

    fmt: "Formatter" = FormatterFactory(
        name="f1",
        code="<html><body>{% for record in dataset.data %}<div>{{record.id}}</div>{% endfor %}</body></html>",
        processor=fqn(processors.ToHTML),
        template=None,
        type=processors.TYPE_LIST,
    )
    result = fmt.render({"dataset": dataset})
    content = result.decode()
    assert content == f"<html><body><div>{H1}</div><div>{H2}</div><div>{H3}</div></body></html>"


def test_formatter_htmlpdf_list(dataset):
    from testutils.factories import FormatterFactory

    fmt: "Formatter" = FormatterFactory(
        name="f1",
        code="<html><body>{% for record in dataset.data %}<div>{{record.id}}</div>{% endfor %}</body></html>",
        template=None,
        processor=fqn(processors.ToHTML),
        type=processors.TYPE_LIST,
    )
    result = fmt.render({"dataset": dataset})
    content = result.decode()
    assert content == f"<html><body><div>{H1}</div><div>{H2}</div><div>{H3}</div></body></html>"


@pytest.fixture()
def dataset_with_images(dataset):
    for i, record in enumerate(dataset.data, start=1):
        record["image_url"] = get_image_url(record.id)
    return dataset


@pytest.mark.django_db
def test_image_proxy_integration(client, dataset_with_images):
    # Mock any external calls within `image_proxy_view`
    with (
        patch("hope_country_report.apps.power_query.storage.HopeStorage", return_value="https://example.com/image.jpg"),
        patch("django.core.cache.cache.get", return_value=None),
        patch("django.core.cache.cache.set", return_value=None),
    ):
        image_path = dataset_with_images.data[0].image_path
        response = client.get(reverse("image_proxy", args=[image_path]))
        assert response.status_code == 200
