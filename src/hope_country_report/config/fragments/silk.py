from ..settings import env, MIDDLEWARE

if env("SILK"):
    MIDDLEWARE += [
        "silk.middleware.SilkyMiddleware",
    ]
