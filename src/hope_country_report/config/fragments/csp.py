# CSP
# django-csp >= 4.0 uses the CONTENT_SECURITY_POLICY dict format.
# The legacy CSP_* top-level settings are no longer honored and only emit
# a warning via the csp.E001 system check.
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
    },
}
