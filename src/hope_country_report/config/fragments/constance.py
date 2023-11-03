from ..settings import env

CONSTANCE_BACKEND = "constance.backends.database.DatabaseBackend"
# CONSTANCE_DATABASE_CACHE_BACKEND = "default"

CONSTANCE_ADDITIONAL_FIELDS = {
    "html_minify_select": [
        "bitfield.forms.BitFormField",
        {"initial": 0, "required": False, "choices": (("html", "HTML"), ("line", "NEWLINE"), ("space", "SPACES"))},
    ],
    "email": [
        "django.forms.EmailField",
        {},
    ],
}

ZIP_PASSWORD_EMAIL_SUBJECT = "Password"
ZIP_PASSWORD_EMAIL_BODY = """
{{ password }}
"""

CONSTANCE_CONFIG = {
    "MINIFY_RESPONSE": (0, "select yes or no", "html_minify_select"),
    "MINIFY_IGNORE_PATH": (r"", "regex for ignored path", str),
    "PQ_SAMPLE_PAGE_SIZE": (100, "PowerQuery sample page size", int),
    "ZIP_PASSWORD_EMAIL_SUBJECT": (ZIP_PASSWORD_EMAIL_SUBJECT, "Email message for zip protected documents", str),
    "ZIP_PASSWORD_EMAIL_BODY": (ZIP_PASSWORD_EMAIL_BODY, "Email message for zip protected documents", str),
    "ZIP_PASSWORD_MAILJET_TEMPLATE": (
        env("ZIP_PASSWORD_MAILJET_TEMPLATE"),
        "Mailjet template ID for zip protected documents",
        str,
    ),
    "CATCH_ALL_EMAIL": (env("CATCH_ALL_EMAIL"), "If set all emails will be sent to this address", "email"),
}
