from ..settings import env  # type: ignore[attr-defined]

CORS_ORIGIN_ALLOW_ALL = env("CORS_ORIGIN_ALLOW_ALL", default=False)
CORS_ALLOWED_ORIGIN_REGEXES = [r"https://\w+.blob.core.windows.net$"]
