# encoding: utf-8
# vim: shiftwidth=4 expandtab

from django import template

register = template.Library()

@register.filter
def none_is_empty(value):
    if value is None:
        return ""
    else:
        return str(value)

