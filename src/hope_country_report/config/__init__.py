from environ import Env

MANDATORY = {
    "DATABASE_HOPE_URL": (str, ""),
    "DATABASE_URL": (str, ""),
    "SECRET_KEY": (str, ""),
}

OPTIONS = {
    "ADMIN_EMAIL": (str, ""),
    "ADMIN_PASSWORD": (str, ""),
    "ALLOWED_HOSTS": (list, ["127.0.0.1", "localhost"]),
    "CELERY_BROKER_URL": (str, ""),
    "DEBUG": (bool, False),
    "EMAIL_HOST_PASSWORD": (str, ""),
    "EMAIL_HOST_USER": (str, ""),
    "STATIC_ROOT": (str, "static/"),
}


class SmartEnv(Env):
    pass
    # def get_value(self, var, cast=None, default=Env.NOTSET, parse_default=False):
    #     return self.get_value(var, cast, default, parse_default)


env = SmartEnv(**MANDATORY, **OPTIONS)
