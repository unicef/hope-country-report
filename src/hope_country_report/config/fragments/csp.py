# Content-Security-Policy (django-csp).
#
# django-csp >= 4.0 uses the CONTENT_SECURITY_POLICY dict format.
# The legacy CSP_* top-level settings are no longer honored and only emit
# a warning via the csp.E001 system check.
#
# `'unsafe-inline'` / `'unsafe-eval'` are still required by the bundled
# admin/editor/charting assets. Migrating away from them (nonces / hashes,
# strict CSP) must be done incrementally; start with CONTENT_SECURITY_POLICY
# in "report-only" mode and monitor before enforcing a stricter policy, see
# https://cheatsheetseries.owasp.org/cheatsheets/Content_Security_Policy_Cheat_Sheet.html
SOURCES = (
    "'self'",
    "'unsafe-eval'",
    "data:",
    "blob:",
    "'unsafe-inline'",
    "d3js.org",
    "raw.githubusercontent.com",
    "cdnjs.cloudflare.com",
    "bl.ocks.org",
    "gist.github.com",
    "gist.githubusercontent.com",
    "unpkg.com",
    "cdn.jsdelivr.net",
    "saunihopedev.blob.core.windows.net",
    "saunihopestg.blob.core.windows.net",
    "saunihopetrn.blob.core.windows.net",
    "saunihopeprd.blob.core.windows.net",
)

CONTENT_SECURITY_POLICY = {
    "DIRECTIVES": {
        "default-src": SOURCES,
        "font-src": SOURCES,
        "frame-src": ["'self'"],
        "object-src": ["'none'"],
        "base-uri": ["'self'"],
    },
    # "EXCLUDE_URL_PREFIXES": ("/admin",),
    # "INCLUDE_NONCE_IN": ("script-src", "style-src"),
}
# CONTENT_SECURITY_POLICY_REPORT_ONLY = {}
