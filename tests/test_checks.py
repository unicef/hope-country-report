from django.apps import apps
from django.test import override_settings


def test_check_models():
    from hope_country_report.apps.hope.checks import check_models

    cfg = apps.get_app_config("admin")
    check_models(cfg)


def test_check_media_storage_ignores_filesystem_storage():
    from hope_country_report.apps.core.checks import check_media_storage

    cfg = apps.get_app_config("admin")
    assert check_media_storage(cfg) == []


def test_check_media_storage_flags_credential_less_azure():
    from hope_country_report.apps.core.checks import check_media_storage

    cfg = apps.get_app_config("admin")
    with override_settings(
        STORAGES={
            "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
            "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
            "media": {"BACKEND": "storages.backends.azure_storage.AzureStorage"},
        },
        MEDIA_AZURE_SAS_TOKEN="",
        MEDIA_AZURE_ACCOUNT_KEY="",
    ):
        errors = check_media_storage(cfg)
    assert len(errors) == 1
    assert errors[0].id == "hcr.W001"


def test_check_media_storage_warns_when_azure_with_credentials():
    from hope_country_report.apps.core.checks import check_media_storage

    cfg = apps.get_app_config("admin")
    with override_settings(
        STORAGES={
            "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
            "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
            "media": {"BACKEND": "storages.backends.azure_storage.AzureStorage"},
        },
        MEDIA_AZURE_SAS_TOKEN="sig=abc",
        MEDIA_AZURE_ACCOUNT_KEY="",
    ):
        errors = check_media_storage(cfg)
    assert len(errors) == 1
    assert errors[0].id == "hcr.W002"
