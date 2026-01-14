"""
Handles streaming events for dataset changes.

The streaming workflow is as follows:

1. A `Query` is marked for streaming by ensuring its related `event`
   object exists and its `enabled` field is set to `True`. This `event`
   object is expected to be found at `query.event`.

2. A `ReportConfiguration` is created and run, which executes the `Query`.
   The result of the execution is saved as a `Dataset` model instance.

3. The `post_save` signal on the `Dataset` model triggers the
   `on_dataset_save_publish_event` handler in this module.

4. The handler checks if `instance.query.event.enabled` is `True`. If it is,
   it converts the `Dataset` data to JSON, creates a streaming `Event`, and
   publishes it with the routing key 'event.routing_key'.

5. Listeners subscribed to routing keys matching 'hcr.*.*' (like the
   'country_report' queue) will receive the broadcast message containing the
   full JSON data of the updated `Dataset`.
"""

import logging
from typing import Any

import tablib
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from sentry_sdk import capture_exception
from streaming.utils import make_event

from hope_country_report.apps.power_query.models import Dataset
from hope_country_report.apps.power_query.utils import to_dataset
from hope_country_report.utils.mail import build_absolute_uri

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Dataset)
def on_dataset_save_publish_event(
    sender: type[Dataset], instance: Dataset, created: bool, **kwargs: dict[str, Any]
) -> None:
    if hasattr(instance.query, "event"):
        try:
            event = instance.query.event
            routing_key = event.get_routing_key()
            if event.enabled:
                from streaming.manager import initialize_engine

                if event.publish_as_url:
                    query = instance.query
                    if not query or not query.country_office:
                        logger.warning(
                            f"Cannot generate URL for Dataset {instance.pk}. It is missing a query or country_office link."
                        )
                        return

                    url_kwargs = {
                        "query__country_office__slug": event.country_office.slug,
                        "query": event.query.pk,
                    }
                    relative_url = reverse("api:dataset-detail", kwargs=url_kwargs)
                    absolute_url = build_absolute_uri(relative_url)
                    message = {"url": absolute_url}
                    if event.office:
                        message["office_slug"] = event.office.slug
                else:
                    ds = to_dataset(instance.data)
                    if isinstance(ds, tablib.Dataset):
                        data = ds.export("json")
                    elif isinstance(ds, dict):
                        data = ds
                    else:
                        raise TypeError("Dataset must be a Dataset or dict")
                    message = {"data": data}
                event = make_event(message=message)
                engine = initialize_engine()
                if not engine.notify(routing_key, event):
                    logger.error("Event notification failed")
            else:
                logger.info(f"Streaming is disabled for Query: '{instance.query.name}'")
        except Exception as e:
            logger.exception(e)
            capture_exception(e)
