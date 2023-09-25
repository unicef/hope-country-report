import os
from pathlib import Path
from typing import Dict

from . import env

SETTINGS_DIR = Path(__file__).parent
PACKAGE_DIR = SETTINGS_DIR.parent
DEVELOPMENT_DIR = PACKAGE_DIR.parent.parent

DEBUG = env.bool("DEBUG")

RO_CONN = dict(**env.db("DATABASE_HOPE_URL")).copy()
# RO_CONN.update(
#     {
#         "OPTIONS": {"options": "-c default_transaction_read_only=on"},
#         "TEST": {
#             "OPTIONS": {"options": ""},
#         },
#     }
# )

DATABASES = {
    "default": env.db(),
    # "hope_no_use": env.db(var="DATABASE_HOPE_URL", default="psql://postgres:pass@db:5432/postgres"),
    "hope_ro": RO_CONN,
}
TEST_RUNNER = "hope_country_report.utils.tests.runner.UnManagedModelTestRunner"
DATABASE_ROUTERS = ("hope_country_report.apps.core.dbrouters.DbRouter",)
DATABASE_APPS_MAPPING: Dict[str, str] = {
    "core": "default",
    "hope": "hope_ro",
}
MIGRATION_MODULES = {"hope": None}

INSTALLED_APPS = [
    # "hope_country_report.apps.c",
    "hope_country_report.web",
    "hope_country_report.web.theme",
    "hope_country_report.apps.tenant.apps.Config",
    "hope_country_report.apps.core.apps.Config",
    "hope_country_report.apps.hope.apps.Config",
    "hope_country_report.apps.pq.apps.Config",
    "django.contrib.contenttypes",
    "smart_admin.apps.SmartTemplateConfig",  # templates
    "smart_admin",  # use this instead of 'django.contrib.admin'
    "smart_admin.apps.SmartLogsConfig",  # optional:  log application
    "smart_admin.apps.SmartAuthConfig",  # optional: django.contrib.auth enhancements
    # "tenant_admin",
    "advanced_filters",
    "django_celery_beat",
    # "power_query.apps.Config",
    "unicef_security",
    "django.contrib.auth",
    "django.contrib.admindocs",
    "django.contrib.humanize",
    "django.contrib.messages",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.sitemaps",
    "django.contrib.staticfiles",
    "django.contrib.gis",
    "django.contrib.postgres",
    # "django.contrib.admin",
    "django_extensions",
    "django_filters",
    "flags",
    "silk",
    "tailwind",
    "push_notifications",
    "rest_framework",
    "rest_framework.authtoken",
    "corsheaders",
    "social_django",
    "admin_extra_buttons",
    "adminactions",
    "adminfilters",
    "adminfilters.depot",
    "import_export",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.middleware.common.CommonMiddleware",
    "tenant_admin.middleware.TenantAdminMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "unicef_security.middleware.UNICEFSocialAuthExceptionMiddleware",
    "hope_country_report.apps.tenant.middleware.TenantAdminMiddleware",
]

AUTHENTICATION_BACKENDS = (
    "unicef_security.backends.UNICEFAzureADB2COAuth2",
    "django.contrib.auth.backends.ModelBackend",
    "hope_country_report.utils.tests.backends.AnyUserAuthBackend",
)

# path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
MEDIA_ROOT = env("MEDIA_ROOT", default="/tmp/media/")
STATIC_ROOT = env("STATIC_ROOT", default=os.path.join(BASE_DIR, "static"))
MEDIA_URL = "/dm-media/"
STATIC_URL = env("STATIC_URL", default="/static/")
STATICFILES_DIRS = []
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

SECRET_KEY = env("SECRET_KEY")
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")

LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_URL = "/accounts/logout"
LOGOUT_REDIRECT_URL = "/"

# TIME_ZONE = env('TIME_ZONE')

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = "en-us"
ugettext = lambda s: s  # noqa
LANGUAGES = (
    ("es", ugettext("Spanish")),  # type: ignore[no-untyped-call]
    ("fr", ugettext("French")),  # type: ignore[no-untyped-call]
    ("en", ugettext("English")),  # type: ignore[no-untyped-call]
    ("ar", ugettext("Arabic")),  # type: ignore[no-untyped-call]
)

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
SITE_ID = 1
INTERNAL_IPS = ["127.0.0.1", "localhost"]

USE_I18N = True
USE_TZ = True

# CACHES = {
#     "default": {
#         "BACKEND": "django.core.cache.backends.redis.RedisCache",
#         "LOCATION": env("REDIS_URL", default="redis://localhost:6379/0"),
#     }
# }

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
DEFAULT_FROM_EMAIL = "hope@unicef.org"
EMAIL_HOST = env("EMAIL_HOST", default="")
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
EMAIL_PORT = env("EMAIL_PORT", default=25)
EMAIL_USE_TLS = env("EMAIL_USE_TLS", default=False)
EMAIL_USE_SSL = env("EMAIL_USE_SSL", default=False)

from .fragments.admin_tenant import *  # noqa
from .fragments.celery import *  # noqa
from .fragments.debug_toolbar import *  # noqa
from .fragments.flags import *  # noqa
from .fragments.power_query import *  # noqa
from .fragments.push_notifications import *  # noqa
from .fragments.rest_framework import *  # noqa
from .fragments.sentry import *  # noqa
from .fragments.smart_admin import *  # noqa
from .fragments.social_auth import *  # noqa
from .fragments.tailwind import *  # noqa
