from django.apps import apps

from hope_country_report.apps.admin.checks import check_models


def test_check_models():
    cfg = apps.get_app_config("admin")
    check_models(cfg)
