from urllib.parse import urlencode

from django.template import Library

register = Library()


@register.simple_tag(takes_context=True)
def build_filter_url(context, field=None, value=None):
    params = context["request"].GET.copy()
    if field:
        if value:
            params[field] = value
        elif field in params:
            del params[field]
    return "?%s" % urlencode(sorted(params.items()))
