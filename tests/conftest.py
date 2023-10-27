import os
import sys
from pathlib import Path

import pytest

import responses

here = Path(__file__).parent
sys.path.insert(0, str(here / "../src"))
sys.path.insert(0, str(here / "extras"))


# os.environ["DJANGO_SETTINGS_MODULE"] = "hope_country_report.config.settings"


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
        "--with-selenium",
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
        AUTHENTICATION_BACKENDS="",
        DEFAULT_FILE_STORAGE="hope_country_report.apps.power_query.storage.DataSetStorage",
        DJANGO_SETTINGS_MODULE="hope_country_report.config.settings",
        CELERY_TASK_ALWAYS_EAGER="1",
        CSRF_COOKIE_SECURE="False",
        SECURE_SSL_REDIRECT="False",
        SECRET_KEY="123",
        MEDIA_ROOT="/tmp/media",
        STATIC_ROOT="/tmp/static",
        SESSION_COOKIE_SECURE="False",
        SESSION_COOKIE_NAME="hcr_test",
        SESSION_COOKIE_DOMAIN="",
    )
    if not config.option.with_sentry:
        os.environ["SENTRY_DSN"] = ""

    if not config.option.enable_selenium:
        config.option.enable_selenium = "selenium" in config.option.markexpr

    if not config.option.enable_selenium:
        config.option.markexpr = "not selenium"

    config.addinivalue_line("markers", "skip_test_if_env(env): this mark skips the tests for the given env")
    _setup_models()
    from django.conf import settings

    settings.MEDIA_ROOT = "/tmp/media"
    settings.STATIC_ROOT = "/tmp/static"
    os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
    os.makedirs(settings.STATIC_ROOT, exist_ok=True)

    from django.core.management import call_command, CommandError

    try:
        call_command("env", check=True)
    except CommandError:
        pytest.exit("FATAL: Environment variables missing")


def pytest_runtest_setup(item):
    driver = item.config.getoption("--driver") or ""

    if driver.lower() == "firefox" and list(item.iter_markers(name="skip_if_firefox")):
        pytest.skip("Test skipped because Firefox")
    if driver.lower() == "safari" and list(item.iter_markers(name="skip_if_safari")):
        pytest.skip("Test skipped because Safari")
    if driver.lower() == "edge" and list(item.iter_markers(name="skip_if_edge")):
        pytest.skip("Test skipped because Edge")

    env_names = [mark.args[0] for mark in item.iter_markers(name="skip_test_if_env")]
    if env_names:
        if item.config.getoption("--env") in os.environ:
            pytest.skip(f"Test skipped because env {env_names!r} is present")


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
def state_context(db):
    from hope_country_report.apps.power_query.defaults import create_defaults, create_periodic_tasks
    from hope_country_report.config.celery import app
    from hope_country_report.state import state

    create_defaults()
    create_periodic_tasks()
    app.control.purge()

    with state.configure():
        yield
