import pytest

from testutils.factories.streaming import EventFactory

pytestmark = pytest.mark.django_db


def test_event_get_routing_key_with_explicit_key():
    event = EventFactory(routing_key="explicit.key.here")
    assert event.get_routing_key() == "explicit.key.here"


def test_event_get_routing_key_with_empty_key():
    event = EventFactory(routing_key="")
    office_code = event.office.code.lower()
    expected_key = f"hcr.{office_code}.dataset.save"
    assert event.get_routing_key() == expected_key
