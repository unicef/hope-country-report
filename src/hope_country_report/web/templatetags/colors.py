import random

from django.template import Library

register = Library()


@register.simple_tag()
def color() -> str:
    return random.choice(["blue", "red", "gray", "yellow", "indigo", "purple"])
