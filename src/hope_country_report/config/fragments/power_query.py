import os

from ..settings import env

POWER_QUERY_DB_ALIAS = "hope_ro"
POWER_QUERY_EXTRA_CONNECTIONS = []
POWER_QUERY_PROJECT_MODEL = "core.CountryOffice"
CELERY_BOOST_FLOWER = env(
    "CELERY_BOOST_FLOWER",
    default=os.environ.get("POWER_QUERY_FLOWER_ADDRESS", "/flower"),
)
