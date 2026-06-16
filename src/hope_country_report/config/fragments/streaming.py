from .. import env

STREAMING_BROKER_URL = env("STREAMING_BROKER_URL")

if STREAMING_BROKER_URL.startswith("amqp://"):
    STREAMING_BROKER_URL = STREAMING_BROKER_URL.replace("amqp://", "rabbit://", 1)

STREAMING = {
    "BROKER_URL": STREAMING_BROKER_URL,
    "MANAGER_CLASS": "streaming.manager.ThreadedChangeManager",
    "DEBUG": env.bool("DEBUG"),
    "QUEUES": {
        "queue_hcr": {
            "name": "queue_hcr",
            "exchange": "django-streaming-broadcast",
            "routing": ["#"],
        }
    },
}
