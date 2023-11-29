from django.apps import apps


def test_check_models():
    from hope_country_report.apps.hope.checks import check_models

    cfg = apps.get_app_config("admin")
    check_models(cfg)
