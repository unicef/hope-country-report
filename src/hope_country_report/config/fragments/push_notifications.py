import json
import logging

from ..settings import env

logger = logging.getLogger(__name__)

PUSH_NOTIFICATIONS_SETTINGS = {
    # "FCM_API_KEY": env("FIREBASE_APIKEY"),
    "GCM_API_KEY": "[your api key]",
    "APNS_CERTIFICATE": "/path/to/your/certificate.pem",
    "APNS_TOPIC": "com.example.push_test",
    "WNS_PACKAGE_SECURITY_ID": "[your package security id, e.g: 'ms-app://e-3-4-6234...']",
    "WNS_SECRET_KEY": "[your app secret key, e.g.: 'KDiejnLKDUWodsjmewuSZkk']",
    "WP_PRIVATE_KEY": env.str("WP_PRIVATE_KEY", multiline=True),
    "WP_CLAIMS": env.str("WP_CLAIMS"),
    "UPDATE_ON_DUPLICATE_REG_ID": True,
    "USER_MODEL": "core.User",
    "UNIQUE_REG_ID": True,
    "WP_APPLICATION_SERVER_KEY": env.str("WP_APPLICATION_SERVER_KEY"),
}
raw = PUSH_NOTIFICATIONS_SETTINGS.get("WP_CLAIMS", "")
try:
    PUSH_NOTIFICATIONS_SETTINGS["WP_CLAIMS"] = json.loads(raw)
except json.JSONDecodeError as e:  # pragma: no cover
    logger.exception(e)
