CONSTANCE_BACKEND = "constance.backends.database.DatabaseBackend"
# CONSTANCE_DATABASE_CACHE_BACKEND = "default"

CONSTANCE_ADDITIONAL_FIELDS = {
    "html_minify_select": [
        "bitfield.forms.BitFormField",
        {"initial": 0, "required": False, "choices": (("html", "HTML"), ("line", "NEWLINE"), ("space", "SPACES"))},
    ],
}

CONSTANCE_CONFIG = {
    "MINIFY_RESPONSE": (0, "select yes or no", "html_minify_select"),
    "MINIFY_IGNORE_PATH": (r"", "regex for ignored path", str),
    "PQ_SAMPLE_PAGE_SIZE": (100, "PowerQuery sample page size", int),
}
