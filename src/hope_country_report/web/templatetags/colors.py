import hashlib
import random

from django.template import Library

register = Library()

COLORS = ["blue", "red", "gray", "yellow", "indigo", "purple"]


@register.simple_tag()
def random_color() -> str:
    return random.choice(COLORS)


@register.filter()
def color(value: str) -> str:
    h = hashlib.md5(value.encode()).hexdigest()
    c = str(bin(int(h, 16))[2:])
    c = sum(int(x) for x in c)
    return COLORS[c % len(COLORS)]
