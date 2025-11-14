from .. import env

# The streaming library uses its own broker URL.
streaming_broker_url = env("STREAMING_BROKER_URL")

# The streaming library expects 'rabbit://' for RabbitMQ, while Celery uses 'amqp://'.
# This ensures compatibility if the user provides a standard amqp:// URL.
if streaming_broker_url.startswith("amqp://"):
    streaming_broker_url = streaming_broker_url.replace("amqp://", "rabbit://", 1)

STREAMING = {
    "BROKER_URL": streaming_broker_url,
    "MANAGER_CLASS": "streaming.manager.ThreadedChangeManager",
    "DEBUG": env.bool("DEBUG"),
    "QUEUES": {
        "queue_hcr": {
            "name": "queue_hcr",
            "exchange": "django-streaming-broadcast",
            "routing_key": "#",
        }
    },
}
