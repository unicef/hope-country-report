from typing import Any

from urllib.parse import urlencode

from django.template import Library
from django.utils.safestring import mark_safe

from adminfilters.utils import parse_bool

register = Library()


@register.simple_tag(takes_context=True)
def build_filter_url(context: dict[str, Any], field: str | None = None, value: str | None = None) -> str:
    params = context["request"].GET.copy()
    if field:
        if value:
            params[field] = value
        elif field in params:
            del params[field]
    return "?%s" % urlencode(sorted(params.items()))


@register.filter("parse_bool")
def _parse_bool(value: Any) -> bool:
    return parse_bool(value)


@register.filter()
def as_bool_icon(value: Any) -> str:
    if parse_bool(value):
        snip = '<div class="icon icon-check1 text-green-400"></div>'
    else:
        snip = '<div class="icon icon-block text-red-400"></div>'
    return mark_safe(snip)
