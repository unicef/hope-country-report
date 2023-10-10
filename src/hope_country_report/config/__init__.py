from typing import Any, Dict, Mapping, reveal_type, Tuple

from environ import Env

MANDATORY = {
    "DATABASE_HOPE_URL": (str, "", "HOPE database connection url (forced to be readonly)"),
    "DATABASE_URL": (str, "", "Database connetcion url"),
    "SECRET_KEY": (str, ""),
    "REDIS_URL": (str, "redis://localhost:6379/0"),
}

DEVELOPMENT = {
    "DEBUG": (bool, True),
}

OPTIONAL = {
    "ADMIN_EMAIL": (str, "", "Admin email"),
    "ADMIN_PASSWORD": (str, "", "Admin password"),
    "ALLOWED_HOSTS": (list, ["127.0.0.1", "localhost"], "Django ALLOWED_HOSTS"),
    "AZURE_ACCOUNT_KEY": (str, "", "Azure account Key"),
    "AZURE_ACCOUNT_NAME": (str, ""),
    "AZURE_CONTAINER": (str, ""),
    "CELERY_BROKER_URL": (str, ""),
    "DEBUG": (bool, False, "Django DEBUG "),
    "DEFAULT_FILE_STORAGE": (str, "django.core.files.storage.FileSystemStorage"),
    "EMAIL_HOST_PASSWORD": (str, ""),
    "EMAIL_HOST_USER": (str, ""),
    "SIGNING_BACKEND": (str, "django.core.signing.TimestampSigner"),
    "STATIC_FILE_STORAGE": (str, "django.contrib.staticfiles.storage.StaticFilesStorage"),
    "MEDIA_URL": (str, "/media/"),
    "MEDIA_ROOT": (str, "/tmp/media/"),
    "STATIC_URL": (str, "/static/"),
    "STATIC_ROOT": (str, "/tmp/static/"),
    "WP_APPLICATION_SERVER_KEY": (str, ""),
    "WP_CLAIMS": (str, '{"sub": "mailto: hope@unicef.org","aud": "https://android.googleapis.com"}'),
    "WP_PRIVATE_KEY": (str, ""),
}


class SmartEnv(Env):
    def __init__(self, **scheme):  # type: ignore[no-untyped-def]
        self.raw = scheme
        super().__init__(**{k: v[:2] for k, v in scheme.items()})


env = SmartEnv(**{**DEVELOPMENT, **MANDATORY, **OPTIONAL})  # type: ignore[arg-type, no-untyped-call]
