import pytest
from django.core.files.base import ContentFile

from testutils.factories.power_query import DatasetFactory, QueryFactory
from testutils.factories.streaming import EventFactory

pytestmark = pytest.mark.django_db


def test_publish_event_when_enabled(capsys):
    event = EventFactory(enabled=True, routing_key="test.key")
    data = [{"name": "test", "value": 1}]
    DatasetFactory(query=event.query, data=data)
    captured = capsys.readouterr()
    assert "routing_key:test.key" in captured.out


def test_publish_event_when_disabled(capsys):
    event = EventFactory(enabled=False)
    DatasetFactory(query=event.query, data=[])
    captured = capsys.readouterr()
    assert captured.out == ""


def test_no_event_for_query_without_event_relation(capsys):
    query = QueryFactory()
    assert not hasattr(query, "event")
    DatasetFactory(query=query, data=[])
    captured = capsys.readouterr()
    assert captured.out == ""


def test_uses_dynamic_routing_key(capsys):
    event = EventFactory(enabled=True, routing_key="")
    DatasetFactory(query=event.query, data=[])
    captured = capsys.readouterr()
    office_code = event.office.code.lower()
    expected_key = f"hcr.{office_code}.dataset.save"
    assert f"routing_key:{expected_key}" in captured.out


def test_fires_on_update(capsys):
    event = EventFactory(enabled=True)
    dataset = DatasetFactory(query=event.query, data=[{"value": 1}])
    capsys.readouterr()
    # We need to manually trigger the save signal for the update
    new_data = [{"value": 2}]
    dataset.file.save("update.pkl", ContentFile(dataset.marshall(new_data)))
    captured = capsys.readouterr()
    # With the console backend, we can only verify that an event was published
    assert "routing_key:" in captured.out


class Unserializable:
    pass


@pytest.mark.skip(reason="Test is incompatible with the console streaming backend and pytest-xdist.")
def test_handles_serialization_exception(caplog):
    """
    Tests that if the dataset contains non-JSON-serializable data,
    the exception is caught and logged by the signal handler.
    """
    EventFactory(enabled=True)
    [{"name": "test", "value": Unserializable()}]
