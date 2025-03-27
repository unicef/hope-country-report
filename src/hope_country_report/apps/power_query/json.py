from typing import Any

from uuid import UUID

from django.core.serializers.json import DjangoJSONEncoder
from django.db import models


class PQJSONEncoder(DjangoJSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, models.Model):
            return str(o)
        if isinstance(o, UUID):
            return o.hex
        return super().default(o)
