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
    "MAILJET_TEMPLATE_ZIP_PASSWORD": (
        env("MAILJET_TEMPLATE_ZIP_PASSWORD"),
        "Mailjet template ID used to send zip password for protected documents",
        str,
    ),
    "MAILJET_TEMPLATE_REPORT_READY": (
        env("MAILJET_TEMPLATE_REPORT_READY"),
        "Mailjet template ID used to notify report execution",
        str,
    ),
    "CATCH_ALL_EMAIL": (env("CATCH_ALL_EMAIL"), "If set all emails will be sent to this address", "email"),
}
