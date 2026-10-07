from django.apps import apps
from django.test import override_settings

AZURE = "storages.backends.azure_storage.AzureStorage"
FILESYSTEM = "django.core.files.storage.FileSystemStorage"


def _storages(default_backend, default_options=None):
    return {
        "default": {"BACKEND": default_backend, "OPTIONS": default_options or {}},
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
    }


def _check(**overrides):
    from hope_country_report.apps.core.checks import check_media_storage

    cfg = apps.get_app_config("admin")
    with override_settings(**overrides):
        return check_media_storage(cfg)


def test_check_models():
    from hope_country_report.apps.hope.checks import check_models

    cfg = apps.get_app_config("admin")
    check_models(cfg)


def test_check_media_storage_ignores_filesystem_storage():
    assert _check(STORAGES=_storages(FILESYSTEM)) == []


def test_check_media_storage_flags_credential_less_azure():
    with override_settings(
        AZURE_ACCOUNT_KEY="",
        AZURE_SAS_TOKEN="",
        AZURE_CONNECTION_STRING="",
    ):
        errors = _check(STORAGES=_storages(AZURE))
    assert [e.id for e in errors] == ["hcr.W001"]


def test_check_media_storage_accepts_options_credentials():
    errors = _check(STORAGES=_storages(AZURE, default_options={"account_key": "secret"}))
    assert [e.id for e in errors] == ["hcr.W002"]

    errors = _check(STORAGES=_storages(AZURE, default_options={"sas_token": "sig=abc"}))
    assert [e.id for e in errors] == ["hcr.W002"]


def test_check_media_storage_accepts_global_credentials():
    with override_settings(AZURE_ACCOUNT_KEY="secret"):
        errors = _check(STORAGES=_storages(AZURE))
    assert [e.id for e in errors] == ["hcr.W002"]
