from typing import TYPE_CHECKING, Any

from django.conf import settings
from django.core.checks import Error, Warning, register

if TYPE_CHECKING:
    from django.apps import AppConfig

AZURE_STORAGE_BACKEND = "storages.backends.azure_storage.AzureStorage"

# Documents are stored through Django's default storage, which is bound to the
# media backend (``FILE_STORAGE_MEDIA``); see STORAGES in config/settings.py.
DOCUMENT_STORAGE_ALIAS = "default"

_CREDENTIAL_OPTION_KEYS = ("account_key", "sas_token", "connection_string", "token_credential")


def _document_storage() -> "dict[str, Any]":
    return (getattr(settings, "STORAGES", {}) or {}).get(DOCUMENT_STORAGE_ALIAS) or {}


def _has_credentials(storage: "dict[str, Any]") -> bool:
    options = storage.get("OPTIONS") or {}
    return any(options.get(key) for key in _CREDENTIAL_OPTION_KEYS)


@register()
def check_media_storage(app_configs: "AppConfig | None", **kwargs: "Any") -> "list[Error|Warning]":
    storage = _document_storage()
    if storage.get("BACKEND") != AZURE_STORAGE_BACKEND:
        return []

    if not _has_credentials(storage):
        return [
            Error(
                "Azure Blob document storage is configured without stored credentials.",
                hint=(
                    "Add account_key/sas_token/connection_string/token_credential to the "
                    "FILE_STORAGE_MEDIA OPTIONS and make sure the container is PRIVATE. Report "
                    "documents must be streamed through the authenticated download views and must "
                    "never be reachable through the public blob endpoint."
                ),
                id="hcr.E001",
            )
        ]

    return [
        Warning(
            "Ensure the Azure media container is private (not publicly readable).",
            hint=(
                "Document files are only reachable through authenticated views, but a "
                "publicly readable container would bypass every permission check on the "
                "blob URL itself. Keep the container private."
            ),
            id="hcr.W002",
        )
    ]
