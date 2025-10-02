import logging
from typing import Any

from django.db.models.signals import post_save
from django.dispatch import receiver
from hope_country_report.apps.power_query.utils import to_dataset
from sentry_sdk import capture_exception
from streaming.utils import make_event

from hope_country_report.apps.power_query.models import Dataset

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Dataset)
def aaa(sender: type[Dataset], instance: Dataset, created: bool, **kwargs: dict[str, Any]) -> None:
    if hasattr(instance.query, "event"):
        try:
            event = instance.query.event
            if event.enabled:
                from streaming.manager import initialize_engine

                ds = to_dataset(instance.data)
                if isinstance(ds, Dataset):
                    data = ds.export("json")
                elif isinstance(ds, dict):
                    data = ds
                else:
                    raise TypeError("Dataset must be a Dataset or dict")
                event = make_event(key="hcr.dataset.save", message={"data": data})
                engine = initialize_engine()
                logger.debug("Stream notification 'hcr.dataset.save'")
                if not engine.notify("hcr.dataset.save", event):
                    logger.error("Event notification failed")
            else:
                logger.debug("Event disabled")
        except Exception as e:
            logger.exception(e)
            capture_exception(e)
