from typing import TYPE_CHECKING, Any

from django.conf import settings
from django.core.checks import Error, Warning, register

if TYPE_CHECKING:
    from django.apps import AppConfig

AZURE_STORAGE_BACKEND = "storages.backends.azure_storage.AzureStorage"

DOCUMENT_STORAGE_ALIASES = ("default", "media")

_CREDENTIAL_OPTION_KEYS = ("account_key", "sas_token", "connection_string", "token_credential")

_CREDENTIAL_SETTINGS = (
    "AZURE_ACCOUNT_KEY",
    "AZURE_SAS_TOKEN",
    "AZURE_CONNECTION_STRING",
    "AZURE_TOKEN_CREDENTIAL",
    "MEDIA_AZURE_ACCOUNT_KEY",
    "MEDIA_AZURE_SAS_TOKEN",
)


def _azure_document_aliases() -> "list[str]":
    storages = getattr(settings, "STORAGES", {}) or {}
    aliases = []
    for alias in DOCUMENT_STORAGE_ALIASES:
        config = storages.get(alias) or {}
        if config.get("BACKEND") == AZURE_STORAGE_BACKEND:
            aliases.append(alias)
    return aliases


def _has_credentials(alias: str) -> bool:
    storages = getattr(settings, "STORAGES", {}) or {}
    options = (storages.get(alias) or {}).get("OPTIONS") or {}
    if any(options.get(key) for key in _CREDENTIAL_OPTION_KEYS):
        return True
    return any(getattr(settings, name, "") for name in _CREDENTIAL_SETTINGS)


@register()
def check_media_storage(app_configs: "AppConfig | None", **kwargs: "Any") -> "list[Error|Warning]":
    aliases = _azure_document_aliases()
    if not aliases:
        return []

    missing = [alias for alias in aliases if not _has_credentials(alias)]
    if missing:
        return [
            Error(
                f"Azure Blob storage for {', '.join(missing)} is configured without stored credentials.",
                hint=(
                    "Provide account_key/sas_token/connection_string/token_credential in the "
                    "storage OPTIONS (or AZURE_ACCOUNT_KEY/AZURE_SAS_TOKEN), and make sure the "
                    "container is PRIVATE. Report documents must be streamed through the "
                    "authenticated download views and must never be reachable through the "
                    "public blob endpoint."
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
