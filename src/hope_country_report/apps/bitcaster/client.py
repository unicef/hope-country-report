import logging
from typing import TYPE_CHECKING, Any

from django.conf import settings
from django.utils.module_loading import import_string

if TYPE_CHECKING:  # pragma: no cover
    from bitcaster_sdk.abstract_client import AbstractClient

logger = logging.getLogger(__name__)

_state: dict[str, "AbstractClient | None"] = {"client": None}


def get_client() -> "AbstractClient | None":
    if _state["client"] is not None:
        return _state["client"]
    if not settings.BITCASTER_ENABLED:
        return None
    bae = settings.BITCASTER_BAE
    org = settings.BITCASTER_ORGANIZATION_SLUG
    project = settings.BITCASTER_PROJECT_SLUG
    application = settings.BITCASTER_APPLICATION_SLUG
    if not all([bae, org, project, application]):
        logger.warning("Bitcaster not fully configured — notifications disabled")
        return None
    client_class = import_string(settings.BITCASTER_CLIENT_CLASS)
    _state["client"] = client_class(
        bae=bae,
        project=project,
        application=application,
    )
    return _state["client"]


def trigger_event(event_name: str, payload: dict[str, Any]) -> None:
    client = get_client()
    if client is None:
        return
    future = client.trigger_event(event_name, context=payload)

    def _on_done(f: Any) -> None:
        if f.exception():
            logger.warning("Bitcaster event failed: %s — %s", event_name, f.exception())

    future.add_done_callback(_on_done)
