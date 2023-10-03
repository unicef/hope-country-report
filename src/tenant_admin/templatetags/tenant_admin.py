from typing import TYPE_CHECKING

from django import template
from django.template import Context as Context, TemplateSyntaxError
from django.template.base import FilterExpression
from django.template.defaulttags import kwarg_re, url as _url, URLNode
from django.urls import reverse

from tenant_admin.config import conf

if TYPE_CHECKING:
    from django.db.models.options import Options

register = template.Library()


# @register.filter
# def admin_urlname(value: "Options", arg: str) -> str:
#     return "%s:%s_%s_%s" % (conf.NAMESPACE, value.app_label, value.model_name, arg)


class TenantURLNode(URLNode):
    def render(self, context: Context) -> str:
        current_app = context.get("current_app", "-")
        if current_app == conf.NAMESPACE:
            args = [arg.resolve(context) for arg in self.args]
            kwargs = {k: v.resolve(context) for k, v in self.kwargs.items()}
            view_name = self.view_name.resolve(context)
            if view_name.startswith("admin:"):
                view_name = view_name.replace("admin:", f"{conf.NAMESPACE}:")
                url = reverse(view_name, args=args, kwargs=kwargs, current_app=current_app)
                return url
        return super().render(context)


@register.tag
def url(parser, token):
    bits = token.split_contents()
    if len(bits) < 2:
        raise TemplateSyntaxError("'%s' takes at least one argument, a URL pattern name." % bits[0])
    viewname = parser.compile_filter(bits[1])
    args = []
    kwargs = {}
    asvar = None
    bits = bits[2:]
    if len(bits) >= 2 and bits[-2] == "as":
        asvar = bits[-1]
        bits = bits[:-2]

    for bit in bits:
        match = kwarg_re.match(bit)
        if not match:
            raise TemplateSyntaxError("Malformed arguments to url tag")
        name, value = match.groups()
        if name:
            kwargs[name] = parser.compile_filter(value)
        else:
            args.append(parser.compile_filter(value))

    return TenantURLNode(viewname, args, kwargs, asvar)
