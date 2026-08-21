import logging

import pytest
from unittest.mock import MagicMock, patch

from hope_country_report.apps.bitcaster.client import _state, get_client, trigger_event


@pytest.fixture(autouse=True)
def reset_client_state():
    _state["client"] = None
    yield
    _state["client"] = None


def test_get_client_disabled():
    assert get_client() is None


def test_get_client_missing_bae_returns_none_and_logs_warning(bitcaster_settings, caplog):
    bitcaster_settings.BITCASTER_BAE = ""
    with caplog.at_level(logging.WARNING, logger="hope_country_report.apps.bitcaster.client"):
        result = get_client()
    assert result is None
    assert "Bitcaster not fully configured" in caplog.text


def test_get_client_returns_client(bitcaster_settings):
    with patch("hope_country_report.apps.bitcaster.client.import_string") as mock_import:
        mock_class = MagicMock()
        mock_instance = MagicMock()
        mock_class.return_value = mock_instance
        mock_import.return_value = mock_class

        result = get_client()

    assert result is mock_instance
    mock_class.assert_called_once_with(
        bae="https://testkey@bitcaster.example.com/api/o/org/",
        project="project",
        application="app",
    )


def test_get_client_caches_singleton(bitcaster_settings):
    with patch("hope_country_report.apps.bitcaster.client.import_string") as mock_import:
        mock_class = MagicMock()
        mock_class.return_value = MagicMock()
        mock_import.return_value = mock_class

        first = get_client()
        second = get_client()

    assert first is second
    mock_class.assert_called_once()


def test_trigger_event_skips_when_no_client():
    with patch("hope_country_report.apps.bitcaster.client.get_client", return_value=None):
        trigger_event("report_completed", {"pk": 1})


def test_trigger_event_calls_client():
    mock_client = MagicMock()
    mock_future = MagicMock()
    mock_client.trigger_event.return_value = mock_future

    with patch("hope_country_report.apps.bitcaster.client.get_client", return_value=mock_client):
        trigger_event("report_completed", {"pk": 1})

    mock_client.trigger_event.assert_called_once_with("report_completed", context={"pk": 1})


def test_trigger_event_callback_no_exception():
    mock_client = MagicMock()
    mock_future = MagicMock()
    mock_future.exception.return_value = None

    def call_callback(fn):
        fn(mock_future)

    mock_future.add_done_callback.side_effect = call_callback
    mock_client.trigger_event.return_value = mock_future

    with patch("hope_country_report.apps.bitcaster.client.get_client", return_value=mock_client):
        trigger_event("report_completed", {})


def test_trigger_event_logs_on_failure(caplog):
    mock_client = MagicMock()
    mock_future = MagicMock()
    mock_future.exception.return_value = Exception("delivery failed")

    def call_callback(fn):
        fn(mock_future)

    mock_future.add_done_callback.side_effect = call_callback
    mock_client.trigger_event.return_value = mock_future

    with patch("hope_country_report.apps.bitcaster.client.get_client", return_value=mock_client):
        with caplog.at_level(logging.WARNING, logger="hope_country_report.apps.bitcaster.client"):
            trigger_event("report_completed", {})

    assert "Bitcaster event failed" in caplog.text
    assert "report_completed" in caplog.text
