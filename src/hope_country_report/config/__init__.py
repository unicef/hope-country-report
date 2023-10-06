from environ import Env

MANDATORY = {
    "DATABASE_HOPE_URL": (str, ""),
    "DATABASE_URL": (str, ""),
    "SECRET_KEY": (str, ""),
    "REDIS_URL": (str, "redis://localhost:6379/0"),
}

OPTIONAL = {
    "ADMIN_EMAIL": (str, ""),
    "SIGNING_BACKEND": (str, "django.core.signing.TimestampSigner"),
    "ADMIN_PASSWORD": (str, ""),
    "ALLOWED_HOSTS": (list, ["127.0.0.1", "localhost"]),
    "CELERY_BROKER_URL": (str, ""),
    "DEBUG": (bool, False),
    "EMAIL_HOST_PASSWORD": (str, ""),
    "EMAIL_HOST_USER": (str, ""),
    "SILK": (bool, False),
    "STATIC_ROOT": (str, "/tmp/static/"),
    "WP_PRIVATE_KEY": (str, ""),
    "WP_APPLICATION_SERVER_KEY": (str, ""),
    "WP_CLAIMS": (str, '{"sub": "mailto: hope@unicef.org","aud": "https://android.googleapis.com"}'),
    "TENANT_IS_MASTER": (bool, False),
}


env = Env(**MANDATORY, **OPTIONAL)
