# # import logging.config
import os
import sys
from pathlib import Path

import pytest
import responses


def _setup_models():
    import django
    from django.conf import settings
    from django.db import connection
    from django.db.backends.utils import truncate_name

    settings.DATABASE_ROUTERS = []

    from django.apps import apps

    django.setup()

    for m in apps.get_app_config("hope").get_models():
        if m._meta.proxy:
            opts = m._meta.proxy_for_model._meta
        else:
            opts = m._meta
        if opts.app_label not in ("contenttypes", "sites"):
            db_table = ("hope_ro__{0.app_label}_{0.model_name}".format(opts)).lower()
            m._meta.db_table = truncate_name(db_table, connection.ops.max_name_length())
            m._meta.db_tablespace = ""
            m._meta.managed = True


def pytest_addoption(parser):
    parser.addoption(
        "--selenium",
        action="store_true",
        dest="enable_selenium",
        default=False,
        help="enable selenium tests",
    )

    parser.addoption(
        "--show-browser",
        "-S",
        action="store_true",
        dest="show_browser",
        default=False,
        help="will not start browsers in headless mode",
    )

    parser.addoption(
        "--with-sentry",
        action="store_true",
        dest="with_sentry",
        default=False,
        help="enable sentry error logging",
    )


def pytest_configure(config):
    here = Path(__file__).parent
    sys.path.insert(0, str(here / "../src"))
    sys.path.insert(0, str(here / "extras"))
    os.environ.update(
        ADMINS="",
        ALLOWED_HOSTS="*",
        ADMIN_URL_PREFIX="acdc/",
        ACCESS_RESTRICTED="false",
        DJANGO_SETTINGS_MODULE="hope_country_report.config.settings",
        ASGI_SERVER="http://testserver:8001",
        CELERY_ALWAYS_EAGER="1",
        CELERY_TASK_ALWAYS_EAGER="1",
        CSRF_COOKIE_SECURE="False",
        FERNET_KEYS="123",
        FRONT_DOOR_ENABLED="False",
        # CACHE_CHAT=
        # STRIPE_SECRET_KEY=os.os.environ['STRIPE_SECRET_KEY'],
        # STRIPE_PUBLIC_KEY=os.os.environ['STRIPE_SECRET_KEY'],
        # STRIPE_JS_URL="http://localhost:8420/js.stripe.com/v3/",
        # STRIPE_WEBHOOK_SECRET="whsec_aaaa",
        TWILIO_SID="twilio-sid",
        TWILIO_TOKEN="twilio-token",
        TWILIO_SERVICE="twilio-service",
        EMAIL_SUBJECT_PREFIX="[Bob-test] ",
        FERNET_USE_HKDF="true",
        SECRET_KEY="123",
        SESSION_COOKIE_SECURE="False",
        STRIPE_SECRET_KEY="sk_test_ithKZS91q4FgBxCJGEqwauqwau",
    )
    if not config.option.with_sentry:
        os.environ["SENTRY_DSN"] = ""

    config.option.enable_selenium = "selenium" in config.option.markexpr

    if not config.option.enable_selenium:
        config.option.markexpr = "not selenium"

    config.addinivalue_line("markers", "skip_if_ci: this mark skips the tests on GitlabCI")
    config.addinivalue_line("markers", "skip_test_if_env(env): this mark skips the tests for the given env")
    _setup_models()


#
# @pytest.fixture(autouse=True)
# def global_setup(
#     request,
#     db,
#     monkeypatch,
#     settings,
#     caplog,
#     django_db_modify_db_settings_parallel_suffix,
# ):
#     caplog.set_level(logging.CRITICAL, logger="django.server")
#
#     settings.STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
#     settings.DEBUG = False
#     settings.SESSION_COOKIE_NAME = "bob_test_session"
#     settings.AUTH_PASSWORD_VALIDATORS = [
#         {
#             "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
#         },
#         {
#             "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
#         },
#         {
#             "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
#         },
#         {
#             "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
#         },
#     ]
#     from django.core.cache import caches
#
#     for backend in caches.all():
#         backend.client.clear()
#
#
@pytest.fixture
def user(db):
    from testutils.factories import UserFactory

    return UserFactory(username="user@example.com", is_active=True)


@pytest.fixture
def office(db):
    from testutils.factories import CountryOfficeFactory

    return CountryOfficeFactory()


#
# @pytest.fixture()
# def django_app_admin(django_app_factory, monkeypatch):
#     from testutils.factories import SuperUserFactory
#
#     django_app = django_app_factory(csrf_checks=False)
#     monkeypatch.setattr("sos.models.User.create_trial", lambda s: True)
#     admin_user = SuperUserFactory(username="superuser")
#     # admin_user.is_active = True
#     # admin_user.is_staff = True
#     # admin_user.is_superuser = True
#     # admin_user.save()
#     django_app.set_user(admin_user)
#     return django_app
#


@pytest.yield_fixture()
def mocked_responses():
    with responses.RequestsMock(assert_all_requests_are_fired=False) as rsps:
        yield rsps
