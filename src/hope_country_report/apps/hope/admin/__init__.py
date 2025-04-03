from django.apps import apps

from hope_country_report.state import state


def register_all_app_models() -> None:
    from django.contrib import admin

    models_to_ignore = [
        "hope.BusinessareaCountries",
    ]
    appconf = apps.get_app_config("hope")

    for model in appconf.get_models():
        try:
            if model._meta.label in models_to_ignore:
                continue
            admin.site.register(model, modeladmin_factory(model))
        except admin.sites.AlreadyRegistered:
            pass


if not state.inspecting:  # pragma: no branch
    from .generic import *  # noqa
    from .utils import modeladmin_factory  # noqa

    register_all_app_models()
