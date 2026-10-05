from django.apps import apps
from django.test import override_settings

AZURE = "storages.backends.azure_storage.AzureStorage"
FILESYSTEM = "django.core.files.storage.FileSystemStorage"

EMPTY_CREDS = {
    "AZURE_ACCOUNT_KEY": "",
    "AZURE_SAS_TOKEN": "",
    "AZURE_CONNECTION_STRING": "",
    "AZURE_TOKEN_CREDENTIAL": None,
    "MEDIA_AZURE_ACCOUNT_KEY": "",
    "MEDIA_AZURE_SAS_TOKEN": "",
}


def _storages(default_backend=FILESYSTEM, media_backend=FILESYSTEM, media_options=None):
    return {
        "default": {"BACKEND": default_backend},
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
        "media": {"BACKEND": media_backend, "OPTIONS": media_options or {}},
    }


def _check(**overrides):
    from hope_country_report.apps.core.checks import check_media_storage

    cfg = apps.get_app_config("admin")
    with override_settings(**{**EMPTY_CREDS, **overrides}):
        return check_media_storage(cfg)


def test_check_models():
    from hope_country_report.apps.hope.checks import check_models

    cfg = apps.get_app_config("admin")
    check_models(cfg)


def test_check_media_storage_ignores_filesystem_storage():
    assert _check() == []


def test_check_media_storage_flags_credential_less_azure():
    errors = _check(STORAGES=_storages(media_backend=AZURE))
    assert [e.id for e in errors] == ["hcr.E001"]


def test_check_media_storage_flags_credential_less_azure_default_alias():
    """The alias actually used by FileFields (``default``) is checked too."""
    errors = _check(STORAGES=_storages(default_backend=AZURE))
    assert [e.id for e in errors] == ["hcr.E001"]


def test_check_media_storage_warns_when_azure_with_flat_credentials():
    errors = _check(STORAGES=_storages(media_backend=AZURE), MEDIA_AZURE_SAS_TOKEN="sig=abc")
    assert [e.id for e in errors] == ["hcr.W002"]


def test_check_media_storage_warns_when_credentials_come_from_options():
    errors = _check(
        STORAGES=_storages(media_backend=AZURE, media_options={"account_key": "secret"}),
    )
    assert [e.id for e in errors] == ["hcr.W002"]


def test_check_media_storage_warns_when_credentials_come_from_azure_settings():
    errors = _check(STORAGES=_storages(media_backend=AZURE), AZURE_ACCOUNT_KEY="secret")
    assert [e.id for e in errors] == ["hcr.W002"]


def test_check_media_storage_warns_when_credentials_come_from_connection_string():
    errors = _check(
        STORAGES=_storages(media_backend=AZURE),
        AZURE_CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=x;AccountKey=y",
    )
    assert [e.id for e in errors] == ["hcr.W002"]
