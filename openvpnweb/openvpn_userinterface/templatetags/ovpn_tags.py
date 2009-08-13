# encoding: utf-8
# vim: shiftwidth=4 expandtab

from django import template
from django.core.urlresolvers import reverse

from openvpnweb.openvpn_userinterface.models import Client

register = template.Library()

def _get_client_id(user):
    try:
        client = Client.objects.get(user=user)
        return client.id
    except Client.DoesNotExist:
        return None

@register.filter
def none_is_empty(value):
    """{{ var|none_is_empty }}
    
    Displays an empty string if var is None. Otherwise the Unicode
    representation of var is displayed.
    """
    return unicode(value) if value is not None else u""

@register.simple_tag
def manage_client_link(user):
    return reverse("manage_client_page", kwargs=dict(
        client_id=_get_client_id(user)
    ))

@register.simple_tag
def remove_client_link(user, group):
    return reverse("remove_client_from_group_page", kwargs=dict(
        client_id=_get_client_id(user),
        group_id=group.id
    ))
