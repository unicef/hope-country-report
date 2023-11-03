from typing import Any, Dict, reveal_type, Tuple

from collections.abc import Mapping

from environ import Env

MANDATORY = {
    "DATABASE_HOPE_URL": (str, "", "HOPE database connection url (forced to be readonly)"),
    "DATABASE_URL": (str, "", "Database connetcion url"),
    "SECRET_KEY": (str, ""),
    "CACHE_URL": (str, "redis://localhost:6379/0"),
    "CELERY_BROKER_URL": (str, "redis://localhost:6379/0"),
    "SENTRY_DSN": (str, ""),
    "SENTRY_URL": (str, "https://excubo.unicef.org/"),
    "SENTRY_ENVIRONMENT": (str, "local"),
    "EMAIL_BACKEND": (str, "anymail.backends.mailjet.EmailBackend"),
    "EMAIL_HOST": (str, ""),
    "EMAIL_HOST_USER": (str, ""),
    "EMAIL_HOST_PASSWORD": (str, ""),
    "EMAIL_PORT": (str, ""),
    "EMAIL_USE_TLS": (str, ""),
    "EMAIL_USE_SSL": (str, ""),
    "MAILJET_API_KEY": (str, ""),
    "MAILJET_SECRET_KEY": (str, ""),
}

DEVELOPMENT = {
    "DEBUG": (bool, True),
    "AUTHENTICATION_BACKENDS": (list, []),
    "SECURE_SSL_REDIRECT": (bool, False),
    "SECURE_HSTS_PRELOAD": (bool, False),
    "CSRF_COOKIE_SECURE": (bool, False),
    "SESSION_COOKIE_SECURE": (bool, False),
}

OPTIONAL = {
    "ADMIN_EMAIL": (str, "", "Admin email"),
    "ADMIN_PASSWORD": (str, "", "Admin password"),
    "ALLOWED_HOSTS": (list, ["127.0.0.1", "localhost"], "Django ALLOWED_HOSTS"),
    "AZURE_ACCOUNT_KEY": (str, "", "Azure account Key"),
    "AZURE_ACCOUNT_NAME": (str, ""),
    "AZURE_CONTAINER": (str, ""),
    "CELERY_VISIBILITY_TIMEOUT": (int, 1800),
    "CELERY_TASK_ALWAYS_EAGER": (bool, False),
    "CELERY_TASK_EAGER_PROPAGATES": (bool, True),
    "CSRF_COOKIE_SECURE": (bool, True),
    "DEBUG": (bool, False, "Django DEBUG"),
    # "DEFAULT_FILE_STORAGE": (str, "django.core.files.storage.FileSystemStorage"),
    "DEFAULT_FILE_STORAGE": (str, "hope_country_report.apps.power_query.storage.DataSetStorage"),
    "EMAIL_HOST_PASSWORD": (str, ""),
    "EMAIL_HOST_USER": (str, ""),
    "SECURE_HSTS_SECONDS": (int, 60),
    "SESSION_COOKIE_HTTPONLY": (bool, True),
    "SECURE_SSL_REDIRECT": (bool, True),
    "SECURE_HSTS_PRELOAD": (bool, True),
    "SIGNING_BACKEND": (str, "django.core.signing.TimestampSigner"),
    "STATIC_FILE_STORAGE": (str, "django.contrib.staticfiles.storage.StaticFilesStorage"),
    "MEDIA_URL": (str, "/media/"),
    "MEDIA_ROOT": (str, "/tmp/media/"),
    "SENTRY_DSN": (str, ""),
    "SENTRY_URL": (str, "https://excubo.unicef.org/"),
    "SENTRY_ENVIRONMENT": (str, "local"),
    "SESSION_COOKIE_DOMAIN": (str, "unicef.org"),
    "SESSION_COOKIE_NAME": (str, "hcr_session"),
    "SESSION_COOKIE_PATH": (str, "/"),
    "SESSION_COOKIE_SECURE": (bool, True),
    "STATIC_URL": (str, "/static/"),
    "STATIC_ROOT": (str, "/tmp/static/"),
    "TIME_ZONE": (str, "UTC"),
    "WP_APPLICATION_SERVER_KEY": (str, ""),
    "WP_CLAIMS": (str, '{"sub": "mailto: hope@unicef.org","aud": "https://android.googleapis.com"}'),
    "WP_PRIVATE_KEY": (str, ""),
}


class SmartEnv(Env):
    def __init__(self, **scheme):  # type: ignore[no-untyped-def]
        self.raw = scheme
        super().__init__(**{k: v[:2] for k, v in scheme.items()})


env = SmartEnv(**{**DEVELOPMENT, **MANDATORY, **OPTIONAL})  # type: ignore[no-untyped-call]
