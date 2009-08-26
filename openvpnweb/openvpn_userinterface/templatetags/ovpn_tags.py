# encoding: utf-8
# vim: shiftwidth=4 expandtab

from django import template
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.template.loader import render_to_string

from openvpnweb.openvpn_userinterface.models import Client, Org

register = template.Library()

def _get_client_id(user):
    try:
        client = Client.objects.get(user=user)
        return client.id
    except Client.DoesNotExist:
        return None

def _get_user_info(user_or_client):
    if isinstance(user_or_client, User):
        user = user_or_client
        return user.username, user.get_full_name()
    else:
        # Assume Client
        client = user_or_client
        return _get_user_info(client.user)

@register.filter
def none_is_empty(value):
    """{{ var|none_is_empty }}
    
    Displays an empty string if var is None. Otherwise the Unicode
    representation of var is displayed.
    """
    return unicode(value) if value is not None else u""

def _format_username(user_or_client):
    username, full_name = _get_user_info(user_or_client)
    if full_name:
        return u"%s (%s)" % (full_name, username)
    else:
        return username

@register.simple_tag
def format_username(user_or_client):
    return _format_username(user_or_client)

@register.simple_tag
def manage_client_link(user_or_client):
    formatted_name = _format_username(user_or_client)
    manage_url = reverse("manage_client_page",
        kwargs={"client_id" : _get_client_id(user_or_client)})
    return u'<a href="%s">%s</a>' % (manage_url, formatted_name)

@register.simple_tag
def remove_client_link(user, group_or_org):
    if isinstance(group_or_org, Org):
        org = group_or_org
        return reverse("remove_client_from_org_page", kwargs=dict(
            client_id=_get_client_id(user),
            org_id=org.id
        ))
    else:
        group = group_or_org
        return reverse("remove_client_from_group_page", kwargs=dict(
            client_id=_get_client_id(user),
            group_id=group.id
        ))

@register.simple_tag
def trivial_form(form, post_url="", submit_text="Save"):
    return render_to_string("openvpn_userinterface/trivial_form.html", {
        "form" : form,
        "post_url" : post_url,
        "submit_text" : submit_text,    
    })