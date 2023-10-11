# # import logging.config
import os
import sys
from pathlib import Path

import pytest
import responses

here = Path(__file__).parent
sys.path.insert(0, str(here / "../src"))
sys.path.insert(0, str(here / "extras"))


def _setup_models():
    import django
    from django.apps import apps
    from django.conf import settings
    from django.db import connection
    from django.db.backends.utils import truncate_name
    from django.db.models import Model

    settings.POWER_QUERY_DB_ALIAS = "default"
    settings.DATABASES["default"]["NAME"] = "_hcr"
    settings.DATABASES["default"]["TEST"] = {"NAME": "_hcr"}
    settings.DATABASE_ROUTERS = ()
    del settings.DATABASES["hope_ro"]

    # settings.DATABASES["hope_ro"]["NAME"] = "_hope"
    # settings.DATABASES["hope_ro"]["TEST"] = {"NAME": "_hope"}
    # settings.DATABASES["hope_ro"]["OPTIONS"] = {}

    django.setup()

    for m in apps.get_app_config("hope").get_models():
        if m._meta.proxy:
            opts = m._meta.proxy_for_model._meta
        else:
            opts = m._meta
        if opts.app_label not in ("contenttypes", "sites"):
            db_table = ("_hope_ro__{0.app_label}_{0.model_name}".format(opts)).lower()
            m._meta.db_table = truncate_name(db_table, connection.ops.max_name_length())
            # m._meta.db_tablespace = ""
            m._meta.managed = True
            m.save = Model.save


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
    os.environ.update(
        ADMINS="",
        ALLOWED_HOSTS="*",
        DJANGO_SETTINGS_MODULE="hope_country_report.config.settings",
        CELERY_TASK_ALWAYS_EAGER="1",
        CSRF_COOKIE_SECURE="False",
        SECRET_KEY="123",
        SESSION_COOKIE_SECURE="False",
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
def country_office(db):
    from testutils.factories import CountryOfficeFactory

    return CountryOfficeFactory()


@pytest.fixture
def reporters(db, country_office, user):
    from hope_country_report.apps.core.utils import get_or_create_reporter_group

    return get_or_create_reporter_group()


@pytest.fixture()
def tenant_user(country_office, reporters):
    """User with access to a tenant"""
    from testutils.factories import UserFactory, UserRoleFactory

    u = UserFactory(username="user", is_staff=False, is_superuser=False, is_active=True)
    UserRoleFactory(country_office=country_office, group=reporters, user=u)
    return u


@pytest.fixture()
def pending_user(db):
    """User with no tenants configured"""

    from testutils.factories import UserFactory

    u = UserFactory(username="pending_user", is_staff=False, is_superuser=False, is_active=True)
    return u


@pytest.fixture()
def mocked_responses():
    with responses.RequestsMock(assert_all_requests_are_fired=False) as rsps:
        yield rsps


@pytest.fixture(autouse=True)
def state_context():
    from hope_country_report.state import state

    with state.configure():
        yield
