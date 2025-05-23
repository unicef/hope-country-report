import os
from pathlib import Path
from urllib.parse import urlparse

import django_stubs_ext

from . import env

SETTINGS_DIR = Path(__file__).parent  # .../src/hope_country_report/config
PACKAGE_DIR = SETTINGS_DIR.parent  # .../src/hope_country_report/
SOURCE_DIR = PACKAGE_DIR.parent.parent  # .../src

DEBUG = env.bool("DEBUG")

RO_CONN = dict(**env.db("DATABASE_HOPE_URL")).copy()
RO_CONN.update(OPTIONS={"options": "-c default_transaction_read_only=on"})

DATABASES = {
    "default": env.db(
        "DATABASE_URL",
        default="postgis://postgres:postgres@db:5432/hcr",
        engine="django.contrib.gis.db.backends.postgis",
    ),
    "hope_ro": env.db(
        "DATABASE_HOPE_URL",
        default="postgis://postgres:postgres@hopedb:5432/hopedb?options=-c%20default_transaction_read_only=on",
        engine="django.contrib.gis.db.backends.postgis",
    ),
}
DATABASE_ROUTERS = ("hope_country_report.apps.core.dbrouters.DbRouter",)
DATABASE_APPS_MAPPING: dict[str, str] = {
    "core": "default",
    "hope": "hope_ro",
}

MIGRATION_MODULES = {"hope": None}

STORAGES = {
    "default": env.storage("FILE_STORAGE_DEFAULT"),
    "staticfiles": env.storage("FILE_STORAGE_STATIC"),
    "media": env.storage("FILE_STORAGE_MEDIA"),
    "hope": env.storage("FILE_STORAGE_HOPE"),
}
INSTALLED_APPS = [
    "hope_country_report.web",
    "hope_country_report.web.theme",
    "hope_country_report.apps.hope",
    "hope_country_report.apps.tenant",
    "hope_country_report.apps.power_query",
    "hope_country_report.apps.core",
    "django.contrib.contenttypes",
    # "smart_admin.apps.SmartTemplateConfig",  # templates
    # "smart_admin",  # use this instead of 'django.contrib.admin'
    # "smart_admin.apps.SmartLogsConfig",  # optional:  log application
    # "smart_admin.apps.SmartAuthConfig",  # optional: django.contrib.auth enhancements
    "advanced_filters",
    "constance",
    "taggit",
    "django_celery_beat",
    "django_filters",
    "admin_cursor_paginator",
    "django_celery_results",
    "unicef_security",
    "django_cleanup.apps.CleanupSelectedConfig",
    "debug_toolbar",
    "jsoneditor",
    "leaflet",
    "django.contrib.auth",
    "django.contrib.humanize",
    "django.contrib.messages",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.sitemaps",
    "django.contrib.staticfiles",
    "django.contrib.gis",
    "django.contrib.postgres",
    "hope_country_report.apps.admin",
    "push_notifications",
    # "django.contrib.admin",
    "django_extensions",
    # # "django_filters",
    "django_select2",
    "chartjs",
    "djgeojson",
    "flags",
    "silk",
    "tailwind",
    "rest_framework",
    "rest_framework.authtoken",
    "rest_framework_gis",
    "corsheaders",
    "social_django",
    "admin_extra_buttons",
    "django_celery_boost",
    "adminactions",
    "adminfilters",
    "adminfilters.depot",
    "smart_env",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "csp.middleware.CSPMiddleware",
    "hope_country_report.middleware.state.StateSetMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "hope_country_report.middleware.user_language.UserLanguageMiddleware",
    "hope_country_report.middleware.silk.SilkMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "unicef_security.middleware.UNICEFSocialAuthExceptionMiddleware",
    "hope_country_report.middleware.exception.ExceptionMiddleware",
    "hope_country_report.middleware.state.StateClearMiddleware",
]

AUTHENTICATION_BACKENDS = (
    *env("AUTHENTICATION_BACKENDS"),
    "social_core.backends.azuread_tenant.AzureADTenantOAuth2",
    "hope_country_report.apps.power_query.backends.PowerQueryBackend",
    "hope_country_report.apps.tenant.backend.TenantBackend",
    "django.contrib.auth.backends.ModelBackend",
)

# path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
MEDIA_ROOT = env("MEDIA_ROOT")
MEDIA_URL = env("MEDIA_URL")
STATIC_ROOT = env("STATIC_ROOT")
STATIC_URL = env("STATIC_URL")
STATICFILES_DIRS = []
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

SECRET_KEY = env("SECRET_KEY")
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")

X_FRAME_OPTIONS = "SAMEORIGIN"

# SECURE_HSTS_SECONDS = 60
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_SSL_REDIRECT = env("SECURE_SSL_REDIRECT")
# SECURE_HSTS_PRELOAD = env("SECURE_HSTS_PRELOAD")
# CSRF_COOKIE_SECURE = env("CSRF_COOKIE_SECURE")
#
SESSION_COOKIE_SECURE = env("SESSION_COOKIE_SECURE")
SESSION_COOKIE_PATH = env("SESSION_COOKIE_PATH")
SESSION_COOKIE_DOMAIN = env("SESSION_COOKIE_DOMAIN")
# SESSION_COOKIE_HTTPONLY = env("SESSION_COOKIE_HTTPONLY")
SESSION_COOKIE_NAME = env("SESSION_COOKIE_NAME")
# SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"

LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_URL = "/accounts/logout"
LOGOUT_REDIRECT_URL = "/"

TIME_ZONE = env("TIME_ZONE")

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = "en-us"
ugettext = lambda s: s  # noqa
LANGUAGES = (
    ("es", ugettext("Spanish")),  # type: ignore[no-untyped-call]
    ("fr", ugettext("French")),  # type: ignore[no-untyped-call]
    ("en", ugettext("English")),  # type: ignore[no-untyped-call]
    ("ar", ugettext("Arabic")),  # type: ignore[no-untyped-call]
    # ("pt", ugettext("Portuguese")),  # type: ignore[no-untyped-call]
)

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
SITE_ID = 1
INTERNAL_IPS = ["127.0.0.1", "localhost"]

USE_I18N = True
USE_TZ = True
LOCALE_PATHS = [PACKAGE_DIR / "LOCALE"]

CACHE_URL = env("CACHE_URL")
REDIS_URL = urlparse(CACHE_URL).hostname
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": CACHE_URL,
    },
    "select2": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": CACHE_URL,
    },
}

ROOT_URLCONF = "hope_country_report.config.urls"
WSGI_APPLICATION = "hope_country_report.config.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [str(PACKAGE_DIR / "templates")],
        "APP_DIRS": False,
        "OPTIONS": {
            "loaders": [
                "django.template.loaders.app_directories.Loader",
            ],
            "context_processors": [
                "constance.context_processors.config",
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "social_django.context_processors.backends",
                "social_django.context_processors.login_redirect",
                "hope_country_report.web.context_processors.state",
            ],
            "libraries": {
                "staticfiles": "django.templatetags.static",
                "i18n": "django.templatetags.i18n",
            },
        },
    },
]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler", "level": "INFO"},
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
}

AUTH_USER_MODEL = "core.User"

HOST = env("HOST", default="http://localhost:8000")
SIGNING_BACKEND = env("SIGNING_BACKEND")

CATCH_ALL_EMAIL = env("CATCH_ALL_EMAIL", default="")
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL")
EMAIL_BACKEND = env("EMAIL_BACKEND")
EMAIL_HOST = env("EMAIL_HOST")
EMAIL_HOST_USER = env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
EMAIL_PORT = env("EMAIL_PORT")
EMAIL_USE_TLS = env("EMAIL_USE_TLS")
EMAIL_USE_SSL = env("EMAIL_USE_SSL")


from .fragments.anymail import *  # noqa
from .fragments.app import *  # noqa
from .fragments.celery import *  # noqa
from .fragments.constance import *  # noqa
from .fragments.cors import *  # noqa
from .fragments.csp import *  # noqa
from .fragments.debug_toolbar import *  # noqa
from .fragments.flags import *  # noqa
from .fragments.hijack import *  # noqa
from .fragments.jsoneditor import *  # noqa
from .fragments.leaflet import *  # noqa
from .fragments.power_query import *  # noqa
from .fragments.push_notifications import *  # noqa
from .fragments.rest_framework import *  # noqa
from .fragments.select2 import *  # noqa
from .fragments.sentry import *  # noqa
from .fragments.silk import *  # noqa
from .fragments.smart_admin import *  # noqa
from .fragments.social_auth import *  # noqa
from .fragments.taggit import *  # noqa
from .fragments.tailwind import *  # noqa

django_stubs_ext.monkeypatch()
