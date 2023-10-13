import os

from django.conf import settings

import sentry_sdk
from celery import Celery, signals

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hope_country_report.config.settings")
app = Celery("hcr")

app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS, related_name="celery_tasks")


@signals.celeryd_init.connect
def init_sentry(**_kwargs):
    sentry_sdk.set_tag("celery", True)
