# CSP
SOURCES = (
    "'self'",
    "'unsafe-eval'",
    # "inline",
    # "unsafe-inline",
    "data:",
    "blob:",
    "'unsafe-inline'",
    # "img-src",
    # "localhost:8000",
    # "unpkg.com",
    # "browser.sentry-cdn.com",
    # "cdnjs.cloudflare.com",
    "d3js.org",
    "raw.githubusercontent.com",
    "unpkg.com",
    "cdn.jsdelivr.net",
)
CSP_DEFAULT_SRC = SOURCES
CSP_FRAME_SRC = []
# CSP_SCRIPT_SRC = SOURCES
# CSP_STYLE_SRC = (
#     "'self'",
#     "'data'",
#     "'unsafe-inline'",
#     "https://unpkg.com",
#     "http://localhost:8000",
#     "https://cdnjs.cloudflare.com",
#     "http://cdnjs.cloudflare.com",
#
# )
# CSP_OBJECT_SRC = ("self",)
# CSP_BASE_URI = ("self", "http://localhost:8000",)
# CSP_CONNECT_SRC = ("self",)
# CSP_FONT_SRC = ("self",)
# CSP_FRAME_SRC = ("self",)
CSP_IMG_SRC = (
    "'self'",
    "data:",
    "openstreetmap.org",
    "unpkg.com",
    "*.tiles.mapbox.com",
    "*.tile.openstreetmap.org",
    "www.openstreetmap.org",
    "basemap.nationalmap.gov",
    "*.tile.maps.openaip.net",
    "tiles.stadiamaps.com",
)
# CSP_MANIFEST_SRC = ("self",)
# CSP_MEDIA_SRC = ("self",)
# CSP_REPORT_URI = ("https://624948b721ea44ac2a6b4de4.endpoint.csper.io/?v=0;",)
# CSP_WORKER_SRC = ("self",)
# """default-src 'self';
# script-src 'report-sample' 'self';
# style-src 'report-sample' 'self';
# object-src 'none';
# base-uri 'self';
# connect-src 'self';
# font-src 'self';
# frame-src 'self';
# img-src 'self';
# manifest-src 'self';
# media-src 'self';
# report-uri https://624948b721ea44ac2a6b4de4.endpoint.csper.io/?v=0;
# worker-src 'none';
# """

# CSP_INCLUDE_NONCE_IN = env("CSP_INCLUDE_NONCE_IN")
# CSP_REPORT_ONLY = env("CSP_REPORT_ONLY")
# CSP_DEFAULT_SRC = env("CSP_DEFAULT_SRC")
# CSP_SCRIPT_SRC = env("CSP_SCRIPT_SRC")
