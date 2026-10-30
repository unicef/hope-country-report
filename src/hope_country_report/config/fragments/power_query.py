from ..settings import env

POWER_QUERY_DB_ALIAS = "hope_ro"
POWER_QUERY_EXTRA_CONNECTIONS = []
POWER_QUERY_PROJECT_MODEL = "core.CountryOffice"
POWER_QUERY_FLOWER_ADDRESS = env("POWER_QUERY_FLOWER_ADDRESS", default="http://localhost:5555")
# "inline": execute query code in the requesting web/worker process (legacy).
# "runner": dispatch previews to the dedicated runner queue; the web process never execs.
POWER_QUERY_EXECUTION_MODE = env("POWER_QUERY_EXECUTION_MODE")
# Set to True only in the dedicated runner deployment. The runner must use a
# clone/scratch app DB, a read-only HOPE clone and no production secrets.
POWER_QUERY_RUNNER = env("POWER_QUERY_RUNNER")
POWER_QUERY_RUNNER_QUEUE = env("POWER_QUERY_RUNNER_QUEUE")
CELERY_BOOST_FLOWER = env("CELERY_BOOST_FLOWER", default="http://localhost:5555")
