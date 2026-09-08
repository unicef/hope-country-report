from typing import TYPE_CHECKING, Any

from django.conf import settings
from django.core.checks import Error, Warning, register

if TYPE_CHECKING:
    from django.apps import AppConfig

AZURE_MEDIA_BACKEND = "storages.backends.azure_storage.AzureStorage"


@register()
def check_media_storage(app_configs: "AppConfig | None", **kwargs: "Any") -> "list[Error|Warning]":
    errors: list = []
    try:
        media_backend = settings.STORAGES["media"]["BACKEND"]
    except (KeyError, TypeError):
        media_backend = None

    if media_backend == AZURE_MEDIA_BACKEND:
        sas_token = getattr(settings, "MEDIA_AZURE_SAS_TOKEN", "")
        account_key = getattr(settings, "MEDIA_AZURE_ACCOUNT_KEY", "")
        if not (sas_token or account_key):
            errors.append(
                Error(
                    "Azure Blob media storage is configured without stored credentials.",
                    hint=(
                        "Set MEDIA_AZURE_SAS_TOKEN or MEDIA_AZURE_ACCOUNT_KEY and make sure the "
                        "container is PRIVATE. Report documents must be streamed through the "
                        "authenticated download views and must never be reachable through the "
                        "public blob endpoint."
                    ),
                    id="hcr.W001",
                )
            )
        else:
            errors.append(
                Warning(
                    "Ensure the Azure media container is private (not publicly readable).",
                    hint=(
                        "Document files are only reachable through authenticated views, but a "
                        "publicly readable container would bypass every permission check on the "
                        "blob URL itself. Keep the container private."
                    ),
                    id="hcr.W002",
                )
            )
    return errors
