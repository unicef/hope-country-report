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

    database_name = "_test_hcr"
    settings.POWER_QUERY_DB_ALIAS = "default"
    settings.DATABASES["default"]["NAME"] = database_name
    settings.DATABASES["default"]["TEST"] = {"NAME": database_name}
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

    parser.addoption(
        "--sentry-environment",
        action="store",
        dest="sentry_environment",
        default="test",
        help="set sentry environment",
    )


def pytest_configure(config):
    os.environ.update(
        ADMINS="",
        ALLOWED_HOSTS="*",
        AUTHENTICATION_BACKENDS="",
        DEFAULT_FILE_STORAGE="hope_country_report.apps.power_query.storage.DataSetStorage",
        STATIC_FILE_STORAGE="hope_country_report.apps.power_query.storage.DataSetStorage",
        DJANGO_SETTINGS_MODULE="hope_country_report.config.settings",
        CATCH_ALL_EMAIL="",
        CELERY_TASK_ALWAYS_EAGER="1",
        CSRF_COOKIE_SECURE="False",
        EMAIL_BACKEND="",
        EMAIL_HOST="",
        EMAIL_HOST_PASSWORD="",
        EMAIL_HOST_USER="",
        EMAIL_PORT="",
        EMAIL_USE_SSL="",
        EMAIL_USE_TLS="",
        MAILJET_API_KEY="",
        MAILJET_SECRET_KEY="",
        MAILJET_TEMPLATE_REPORT_READY="",
        MAILJET_TEMPLATE_ZIP_PASSWORD="",
        MEDIA_ROOT="/tmp/media",
        SECURE_HSTS_PRELOAD="False",
        SECURE_SSL_REDIRECT="False",
        SECRET_KEY="123",
        SENTRY_ENVIRONMENT="",
        SENTRY_URL="",
        SESSION_COOKIE_SECURE="False",
        SESSION_COOKIE_NAME="hcr_test",
        SESSION_COOKIE_DOMAIN="",
        STATIC_ROOT="/tmp/static",
        SIGNING_BACKEND="django.core.signing.TimestampSigner",
        WP_PRIVATE_KEY="",
    )
    if not config.option.with_sentry:
        os.environ["SENTRY_DSN"] = ""
    else:
        os.environ["SENTRY_ENVIRONMENT"] = config.option.sentry_environment

    if not config.option.enable_selenium:
        config.option.enable_selenium = "selenium" in config.option.markexpr

    # if not config.option.enable_selenium:
    #     if config.option.markexpr:
    #         config.option.markexpr = "not selenium"
    #     elif config.option.markexpr:
    #         config.option.markexpr += " and not selenium"

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


def pytest_collection_modifyitems(config, items):
    if not config.option.enable_selenium:
        skip_mymarker = pytest.mark.skip(reason="selenium not enabled")
        for item in items:
            if list(item.iter_markers(name="selenium")):
                item.add_marker(skip_mymarker)


@pytest.fixture
def user(db):
    from testutils.factories import UserFactory

    return UserFactory(username="user@example.com", is_active=True)


@pytest.fixture()
def afghanistan(db):
    from testutils.factories import CountryOfficeFactory

    return CountryOfficeFactory(name="Afghanistan")


@pytest.fixture
def reporters(db, afghanistan, user):
    from hope_country_report.apps.core.utils import get_or_create_reporter_group

    return get_or_create_reporter_group()


@pytest.fixture()
def tenant_user(afghanistan, reporters):
    """User with access to a tenant"""
    from testutils.factories import UserFactory, UserRoleFactory

    u = UserFactory(username="user", is_staff=False, is_superuser=False, is_active=True)
    UserRoleFactory(country_office=afghanistan, group=reporters, user=u)
    return u


@pytest.fixture()
def pending_user(db):
    """User with no tenants configured"""

    from testutils.factories import UserFactory

    u = UserFactory(username="pending_user", is_staff=False, is_superuser=False, is_active=True)
    return u


@pytest.fixture()
def afg_user(user, afghanistan):
    from testutils.perms import user_grant_permissions

    grant = user_grant_permissions(
        user,
        [
            "power_query.view_reportconfiguration",
            "power_query.view_reportdocument",
        ],
        afghanistan,
    )
    grant.start()
    user._afghanistan = afghanistan
    yield user
    grant.stop()


@pytest.fixture()
def mocked_responses():
    with responses.RequestsMock(assert_all_requests_are_fired=False) as rsps:
        yield rsps


@pytest.fixture(autouse=True)
def state_context(db):
    from testutils.utils import set_flag

    from hope_country_report.apps.core.utils import get_or_create_reporter_group
    from hope_country_report.apps.power_query.defaults import create_defaults, create_periodic_tasks
    from hope_country_report.config.celery import app
    from hope_country_report.state import state

    create_defaults()
    create_periodic_tasks()
    get_or_create_reporter_group()

    app.control.purge()
    set_flag("LOCAL_LOGIN", True).start()
    with state.configure():
        yield
