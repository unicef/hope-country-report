from ..settings import env

POWER_QUERY_DB_ALIAS = "hope_ro"
POWER_QUERY_EXTRA_CONNECTIONS = []
POWER_QUERY_PROJECT_MODEL = "core.CountryOffice"
POWER_QUERY_FLOWER_ADDRESS = env("POWER_QUERY_FLOWER_ADDRESS", default="http://localhost:5555")
