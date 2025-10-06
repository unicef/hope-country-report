from .. import env

STREAMING = {"BROKER_URL": env("STREAMING_BROKER_URL"), "QUEUES": {"country_report": {"routing": ["hcr.*.*"]}}}
