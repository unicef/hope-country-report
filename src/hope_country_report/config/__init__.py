from enum import Enum

from smart_env import SmartEnv

DJANGO_HELP_BASE = "https://docs.djangoproject.com/en/5.0/ref/settings"


def setting(anchor):
    return f"@see {DJANGO_HELP_BASE}#{anchor}"


class Group(Enum):
    DJANGO = 1


NOT_SET = "<- not set ->"
EXPLICIT_SET = ["sqlite://", "https://example.com", NOT_SET]


CONFIG = {
    "ADMIN_EMAIL": (str, "", "Initial user created at first deploy"),
    "ADMIN_PASSWORD": (str, "", "Password for initial user created at first deploy"),
    "ALLOWED_HOSTS": (list, ["127.0.0.1", "localhost"], setting("allowed-hosts")),
    "AUTHENTICATION_BACKENDS": (list, [], setting("authentication-backends")),
    "AZURE_ACCOUNT_KEY": (str, ""),
    "AZURE_ACCOUNT_NAME": (str, ""),
    "AZURE_CLIENT_ID": (str, "", "Azure Client ID"),
    "AZURE_CLIENT_KEY": (str, ""),
    "AZURE_CLIENT_SECRET": (str, ""),
    "AZURE_CONTAINER": (str, ""),
    "AZURE_TENANT_ID": (str, ""),
    "AZURE_TENANT_KEY": (str, ""),
    "CACHE_URL": (str, "redis://localhost:6379/0"),
    "CATCH_ALL_EMAIL": (str, ""),
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
    "CORS_ORIGIN_ALLOW_ALL": (bool, False),
    "CSRF_COOKIE_SECURE": (bool, True, setting("csrf-cookie-secure")),
    "DATABASE_HOPE_URL": (str, "sqlite://", "HOPE database connection url (forced to be readonly)"),
    "DATABASE_URL": (
        str,
        "sqlite://",
        "https://django-environ.readthedocs.io/en/latest/types.html#environ-env-db-url",
    ),
    "DEBUG": (bool, False, setting("debug")),
    "DEFAULT_FROM_EMAIL": (str, ""),
    "FILE_STORAGE_DEFAULT": (
        str,
        "django.core.files.storage.FileSystemStorage",
        setting("storages"),
    ),
    "FILE_STORAGE_MEDIA": (
        str,
        "django.core.files.storage.FileSystemStorage",
        setting("storages"),
    ),
    "FILE_STORAGE_STATIC": (
        str,
        "django.contrib.staticfiles.storage.StaticFilesStorage",
        setting("storages"),
    ),
    "FILE_STORAGE_HOPE": (
        str,
        "storages.backends.azure_storage.AzureStorage",
        setting("storages"),
    ),
    "EMAIL_BACKEND": (str, "anymail.backends.mailjet.EmailBackend", "Do not change in prod"),
    "EMAIL_HOST": (str, ""),
    "EMAIL_HOST_PASSWORD": (str, ""),
    "EMAIL_HOST_USER": (str, ""),
    "EMAIL_PORT": (str, ""),
    "EMAIL_USE_SSL": (str, ""),
    "EMAIL_USE_TLS": (str, ""),
    "HOPE_AZURE_ACCOUNT_NAME": (str, ""),
    "HOPE_AZURE_ACCOUNT_KEY": (str, ""),
    "HOPE_AZURE_AZURE_CONTAINER": (str, ""),
    "HOPE_AZURE_SAS_TOKEN": (str, ""),
    "HOST": (str, "http://localhost:8000"),
    "MAILJET_API_KEY": (str, NOT_SET),
    "MAILJET_SECRET_KEY": (str, NOT_SET),
    "MAILJET_TEMPLATE_REPORT_READY": (str, NOT_SET),
    "MAILJET_TEMPLATE_ZIP_PASSWORD": (str, NOT_SET),
    "MEDIA_AZURE_ACCOUNT_NAME": (str, ""),
    "MEDIA_AZURE_ACCOUNT_KEY": (str, ""),
    "MEDIA_AZURE_AZURE_CONTAINER": (str, ""),
    "MEDIA_AZURE_SAS_TOKEN": (str, ""),
    "MEDIA_ROOT": (str, "/tmp/media/", setting("media-root")),
    "MEDIA_URL": (str, "/media/", setting("media-url")),
    "POWER_QUERY_FLOWER_ADDRESS": (str, "http://localhost:5555", "Flower address"),
    "SECRET_KEY": (str, NOT_SET, setting("secret-key")),
    "SECURE_HSTS_PRELOAD": (bool, True, setting("secure-hsts-preload")),
    "SECURE_HSTS_SECONDS": (int, 60, setting("secure-hsts-seconds")),
    "SECURE_SSL_REDIRECT": (bool, True, setting("secure-ssl-redirect")),
    "SENTRY_DSN": (str, "", "https://develop.sentry.dev/config/"),
    "SENTRY_ENVIRONMENT": (str, NOT_SET, "https://develop.sentry.dev/config/"),
    "SENTRY_URL": (str, "https://excubo.unicef.io/sentry/hope-cr/", "Sentry server url"),
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
    "STATIC_ROOT": (str, "/tmp/static/", setting("static-root")),
    "STATIC_URL": (str, "/static/", setting("static-url")),
    "TIME_ZONE": (str, "UTC", setting("std-setting-TIME_ZONE")),
    "WP_APPLICATION_SERVER_KEY": (str, ""),
    "WP_CLAIMS": (str, '{"sub": "mailto: hope@unicef.org","aud": "https://android.googleapis.com"}'),
    "WP_PRIVATE_KEY": (str, ""),
}


env = SmartEnv(**CONFIG)  # type: ignore[no-untyped-call]
