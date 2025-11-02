import pytest

from tests.extras.testutils.factories.power_query import DatasetFactory, QueryFactory
from tests.streaming.factories import EventFactory

pytestmark = pytest.mark.django_db


def test_publish_event_when_enabled(capsys):
    event = EventFactory(enabled=True, routing_key="test.key")
    data = [{"name": "test", "value": 1}]
    DatasetFactory(query=event.query, data=data)
    captured = capsys.readouterr()
    assert '"routing_key": "test.key"' in captured.out
    assert '"data": "[{\\"name\\": \\"test\\", \\"value\\": 1}]"' in captured.out


def test_publish_event_when_disabled(capsys):
    event = EventFactory(enabled=False)
    DatasetFactory(query=event.query)
    captured = capsys.readouterr()
    assert captured.out == ""


def test_no_event_for_query_without_event_relation(capsys):
    query = QueryFactory()
    assert not hasattr(query, "event")
    DatasetFactory(query=query)
    captured = capsys.readouterr()
    assert captured.out == ""


def test_uses_dynamic_routing_key(capsys):
    event = EventFactory(enabled=True, routing_key="")
    DatasetFactory(query=event.query)
    captured = capsys.readouterr()
    office_code = event.office.code.lower()
    expected_key = f"hcr.{office_code}.dataset.save"
    assert f'"routing_key": "{expected_key}"' in captured.out


def test_fires_on_update(capsys):
    dataset = DatasetFactory(query__event__enabled=True, data=[{"value": 1}])
    capsys.readouterr()
    dataset.data = [{"value": 2}]
    dataset.save()
    captured = capsys.readouterr()
    assert '"data": "[{\\"value\\": 2}]"' in captured.out


def test_handles_serialization_exception(caplog):
    """
    Tests that if the dataset contains non-JSON-serializable data,
    the exception is caught and logged by the signal handler.
    """

    class Unserializable:
        pass

    event = EventFactory(enabled=True)
    data = [{"name": "test", "value": Unserializable()}]
    DatasetFactory(query=event.query, data=data)
    assert "is not JSON serializable" in caplog.text
    assert "ERROR" in caplog.text
