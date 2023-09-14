from ..settings import env  # type: ignore[attr-defined]

POWER_QUERY_DB_ALIAS = env("POWER_QUERY_DB_ALIAS", default="hope")
POWER_QUERY_EXTRA_CONNECTIONS = []
FLOWER_ADDRESS = ""
