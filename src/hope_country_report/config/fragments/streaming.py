from .. import env

STREAMING = {
    "BROKER_URL": env("STREAMING_BROKER_URL", "console://", "Streaming Broker URL for Streaming library"),
    "MANAGER_CLASS": "streaming.manager.ThreadedChangeManager",
    "DEBUG": True,
}
