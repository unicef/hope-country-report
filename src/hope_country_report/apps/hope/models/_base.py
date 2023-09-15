from typing import Any, Dict, Iterable, Optional, Tuple

from django.db import models


class HopeModel(models.Model):
    class Meta:
        abstract = True
        managed = False
        app_label = "hope"

    def save(
        self,
        force_insert: bool = ...,
        force_update: bool = ...,
        using: Optional[str] = ...,
        update_fields: Optional[Iterable[str]] = ...,
    ) -> None:
        pass

    def delete(self, using: Any = None, keep_parents: bool = False) -> Tuple[int, Dict[str, int]]:
        return 0, {}
