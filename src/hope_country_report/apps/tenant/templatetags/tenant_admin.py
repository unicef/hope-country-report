from typing import TYPE_CHECKING

from django import template

if TYPE_CHECKING:
    from django.db.models.options import Options

register = template.Library()


@register.filter
def admin_urlname(value: "Options", arg: str) -> str:
    return "admin:%s_%s_%s" % (value.app_label, value.model_name, arg)
