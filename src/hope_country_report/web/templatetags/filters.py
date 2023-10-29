from urllib.parse import urlencode

from django.template import Library

register = Library()

COLORS = ["blue", "red", "gray", "yellow", "indigo", "purple"]


@register.simple_tag(takes_context=True)
def build_filter_url(context, field=None, value=None):
    params = context["request"].GET.copy()
    if field:
        if value:
            params[field] = value
        else:
            del params[field]
    return "?%s" % urlencode(sorted(params.items()))
    # def get_query_string(self, new_params=None, remove=None):
    #     if new_params is None:
    #         new_params = {}
    #     if remove is None:
    #         remove = []
    #     p = self.params.copy()
    #     for r in remove:
    #         for k in list(p):
    #             if k.startswith(r):
    #                 del p[k]
    #     for k, v in new_params.items():
    #         if v is None:
    #             if k in p:
    #                 del p[k]
    #         else:
    #             p[k] = v
    #     return "?%s" % urlencode(sorted(p.items()))
