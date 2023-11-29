from enum import Enum
from typing import Any, Dict, reveal_type, Tuple

from collections.abc import Mapping

from environ import Env

DJANGO_HELP_BASE = "https://docs.djangoproject.com/en/4.2/ref/settings"


def setting(anchor):
    return f"@see {DJANGO_HELP_BASE}#{anchor}"


class Group(Enum):
    DJANGO = 1


NOT_SET = "<- not set ->"
EXPLICIT_SET = ["sqlite://", NOT_SET]


CONFIG = {
    "ADMIN_EMAIL": (str, "", "Initial user created at first deploy"),
    "ADMIN_PASSWORD": (str, "", "Password for initial user created at first deploy"),
    "ALLOWED_HOSTS": (list, ["127.0.0.1", "localhost"], setting("allowed-hosts")),
    "AUTHENTICATION_BACKENDS": (list, [], setting("authentication-backends")),
    "AZURE_ACCOUNT_KEY": (str, ""),
    "AZURE_ACCOUNT_NAME": (str, ""),
    "AZURE_CLIENT_ID": (str, "", "Azure Client ID"),
    "AZURE_CLIENT_SECRET": (str, ""),
    "AZURE_CONTAINER": (str, ""),
    "AZURE_TENANT_KEY": (str, ""),
    "CACHE_URL": (str, "redis://localhost:6379/0"),
    "CATCH_ALL_EMAIL": (str, True),
    "CELERY_BROKER_URL": (
        str,
        NOT_SET,
        "https://docs.celeryq.dev/en/stable/django/first-steps-with-django.html",
    ),
    "CELERY_TASK_ALWAYS_EAGER": (
        bool,
        False,
        "https://docs.celeryq.dev/en/stable/userguide/configuration.html#std-setting-task_always_eager",
    ),
    "CELERY_TASK_EAGER_PROPAGATES": (
        bool,
        True,
        "https://docs.celeryq.dev/en/stable/userguide/configuration.html#task-eager-propagates",
    ),
    "CELERY_VISIBILITY_TIMEOUT": (
        int,
        1800,
        "https://docs.celeryq.dev/en/stable/userguide/configuration.html#broker-transport-options",
    ),
    "CSRF_COOKIE_SECURE": (bool, True, setting("csrf-cookie-secure")),
    "DATABASE_HOPE_URL": (str, "sqlite://", "HOPE database connection url (forced to be readonly)"),
    "DATABASE_URL": (
        str,
        "sqlite://",
        "https://django-environ.readthedocs.io/en/latest/types.html#environ-env-db-url",
    ),
    "DEBUG": (bool, False, setting("debug")),
    "DEFAULT_FILE_STORAGE": (
        str,
        "hope_country_report.apps.power_query.storage.DataSetStorage",
        setting("storages"),
    ),
    "EMAIL_BACKEND": (str, "anymail.backends.mailjet.EmailBackend", "Do not change in prod"),
    "EMAIL_HOST": (str, ""),
    "EMAIL_HOST_PASSWORD": (str, ""),
    "EMAIL_HOST_USER": (str, ""),
    "EMAIL_PORT": (str, ""),
    "EMAIL_USE_SSL": (str, ""),
    "EMAIL_USE_TLS": (str, ""),
    "MAILJET_API_KEY": (str, NOT_SET),
    "MAILJET_SECRET_KEY": (str, NOT_SET),
    "MAILJET_TEMPLATE_REPORT_READY": (str, NOT_SET),
    "MAILJET_TEMPLATE_ZIP_PASSWORD": (str, NOT_SET),
    "MEDIA_ROOT": (str, "/tmp/media/", setting("media-root")),
    "MEDIA_URL": (str, "/media/", setting("media-url")),
    "SECRET_KEY": (str, NOT_SET, setting("secret-key")),
    "SECURE_HSTS_PRELOAD": (bool, True, setting("secure-hsts-preload")),
    "SECURE_HSTS_SECONDS": (int, 60, setting("secure-hsts-seconds")),
    "SECURE_SSL_REDIRECT": (bool, True, setting("secure-ssl-redirect")),
    "SENTRY_DSN": (str, NOT_SET, "https://develop.sentry.dev/config/"),
    "SENTRY_ENVIRONMENT": (str, NOT_SET, "https://develop.sentry.dev/config/"),
    "SENTRY_URL": (str, "https://excubo.unicef.org/", "Sentry server url"),
    "SESSION_COOKIE_DOMAIN": (str, "unicef.org", setting("std-setting-SESSION_COOKIE_DOMAIN")),
    "SESSION_COOKIE_HTTPONLY": (bool, True, setting("session-cookie-httponly")),
    "SESSION_COOKIE_NAME": (str, "hcr_session", setting("session-cookie-name")),
    "SESSION_COOKIE_PATH": (str, "/", setting("session-cookie-path")),
    "SESSION_COOKIE_SECURE": (bool, True, setting("session-cookie-secure")),
    "SIGNING_BACKEND": (str, "django.core.signing.TimestampSigner", setting("signing-backend")),
    "SOCIAL_AUTH_REDIRECT_IS_HTTPS": (
        bool,
        True,
        "https://python-social-auth.readthedocs.io/en/latest/configuration/settings.html",
    ),
    "STATIC_FILE_STORAGE": (
        str,
        "django.contrib.staticfiles.storage.StaticFilesStorage",
        setting("storages"),
    ),
    "STATIC_ROOT": (str, "/tmp/static/", setting("static-root")),
    "STATIC_URL": (str, "/static/", setting("static-url")),
    "TIME_ZONE": (str, "UTC", setting("std-setting-TIME_ZONE")),
    "WP_APPLICATION_SERVER_KEY": (str, ""),
    "WP_CLAIMS": (str, '{"sub": "mailto: hope@unicef.org","aud": "https://android.googleapis.com"}'),
    "WP_PRIVATE_KEY": (str, ""),
}


class SmartEnv(Env):
    def __init__(self, **scheme):  # type: ignore[no-untyped-def]
        self.raw = scheme
        values = {k: v[:2] for k, v in scheme.items()}
        super().__init__(**values)

    def get_help(self, key):
        entry = self.raw.get(key, "")
        if len(entry) > 2:
            return entry[2]

    def get_default(self, var):
        var_name = f"{self.prefix}{var}"
        if var_name in self.scheme:
            var_info = self.scheme[var_name]

            if len(var_info) > 1:
                value = var_info[1]
                cast = var_info[0]
            else:
                cast = var_info
                value = ""

            prefix = b"$" if isinstance(value, bytes) else "$"
            escape = rb"\$" if isinstance(value, bytes) else r"\$"
            if hasattr(value, "startswith") and value.startswith(prefix):
                value = value.lstrip(prefix)
                value = self.get_value(value, cast=cast)

            if self.escape_proxy and hasattr(value, "replace"):
                value = value.replace(escape, prefix)

        return value


env = SmartEnv(**CONFIG)  # type: ignore[no-untyped-call]
