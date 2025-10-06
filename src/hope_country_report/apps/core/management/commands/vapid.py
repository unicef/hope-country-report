from typing import Any

from cryptography.hazmat.primitives import serialization
from django.conf import settings
from django.core.management.base import BaseCommand


def clean_key(value: str) -> str:
    return value.replace("\n", "").replace("-----BEGIN PRIVATE KEY-----", "").replace("-----END PRIVATE KEY-----", "")


class Command(BaseCommand):
    requires_migrations_checks = False
    output_transaction = False
    requires_system_checks = []

    def handle(self, *args: Any, **options: Any) -> str | None:
        from py_vapid import Vapid02

        if not settings.PUSH_NOTIFICATIONS_SETTINGS["WP_PRIVATE_KEY"]:
            vapid = Vapid02(conf=args)
            vapid.generate_keys()
            KEY = clean_key(vapid.private_pem().decode())
        else:
            KEY = clean_key(settings.PUSH_NOTIFICATIONS_SETTINGS["WP_PRIVATE_KEY"])
        vapid = Vapid02.from_string(KEY)
        vapid.public_key.public_bytes(serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint)
        claims = settings.PUSH_NOTIFICATIONS_SETTINGS["WP_CLAIMS"]
        vapid.sign(claims)
