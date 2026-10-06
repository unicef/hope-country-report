import pytest
from django.apps import apps
from django.test import override_settings

AZURE = "storages.backends.azure_storage.AzureStorage"
FILESYSTEM = "django.core.files.storage.FileSystemStorage"


def _storages(default_backend=FILESYSTEM, default_options=None):
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


@pytest.mark.parametrize(
    ("overrides", "expected"),
    [
        pytest.param({}, [], id="filesystem-ignored"),
        pytest.param({"STORAGES": _storages(default_backend=AZURE)}, ["hcr.E001"], id="azure-missing-creds"),
        pytest.param(
            {"STORAGES": _storages(default_backend=AZURE, default_options={"account_key": "secret"})},
            ["hcr.W002"],
            id="options-account-key",
        ),
        pytest.param(
            {"STORAGES": _storages(default_backend=AZURE, default_options={"sas_token": "sig=abc"})},
            ["hcr.W002"],
            id="options-sas-token",
        ),
        pytest.param(
            {
                "STORAGES": _storages(
                    default_backend=AZURE, default_options={"connection_string": "AccountName=x;AccountKey=y"}
                )
            },
            ["hcr.W002"],
            id="options-connection-string",
        ),
    ],
)
def test_check_media_storage(overrides, expected):
    errors = _check(**overrides)
    assert [e.id for e in errors] == expected
