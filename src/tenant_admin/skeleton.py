from __future__ import annotations

from typing import TYPE_CHECKING, List, Type, Union

from django.contrib.admin import ModelAdmin

if TYPE_CHECKING:
    from .options import TenantModelAdmin


class Skeleton:
    default_attrs = [
        "actions",
        "date_hierarchy",
        "filter_horizontal",
        "list_display",
        "list_filter",
        "raw_id_fields",
        "search_fields",
    ]

    def __init__(
        self, model_admin: Type[ModelAdmin], attrs: Union[None, List[str]] = None
    ):
        self.model_admin = model_admin
        self.attributes = self.default_attrs if attrs is None else attrs

    def initialise(self, dest: TenantModelAdmin) -> None:
        for attr in self.attributes:
            if attr not in dest.__class__.__dict__:
                setattr(dest.__class__, attr, getattr(self.model_admin, attr))
