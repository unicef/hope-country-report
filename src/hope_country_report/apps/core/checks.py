from typing import TYPE_CHECKING, Any

from django.conf import settings
from django.core.checks import Error, Warning, register

if TYPE_CHECKING:
    from django.apps import AppConfig

AZURE_STORAGE_BACKEND = "storages.backends.azure_storage.AzureStorage"
DOCUMENT_STORAGE_ALIAS = "default"
_CREDENTIAL_OPTION_KEYS = ("account_key", "sas_token", "connection_string", "token_credential")
_CREDENTIAL_SETTING_KEYS = ("AZURE_ACCOUNT_KEY", "AZURE_SAS_TOKEN", "AZURE_CONNECTION_STRING")


def _document_storage() -> "dict[str, Any]":
    try:
        return settings.STORAGES[DOCUMENT_STORAGE_ALIAS]
    except (KeyError, TypeError):
        return {}


def _has_credentials(storage: "dict[str, Any]") -> bool:
    options = storage.get("OPTIONS") or {}
    if any(options.get(key) for key in _CREDENTIAL_OPTION_KEYS):
        return True
    return any(getattr(settings, key, "") for key in _CREDENTIAL_SETTING_KEYS)


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
                    "FILE_STORAGE_DEFAULT OPTIONS and make sure the container is PRIVATE. Report "
                    "documents must be streamed through the authenticated download views and must "
                    "never be reachable through the public blob endpoint."
                ),
                id="hcr.W001",
            )
        ]

    return [
        Warning(
            "Ensure the Azure document container is private (not publicly readable).",
            hint=(
                "Document files are only reachable through authenticated views, but a "
                "publicly readable container would bypass every permission check on the "
                "blob URL itself. Keep the container private."
            ),
            id="hcr.W002",
        )
    ]
