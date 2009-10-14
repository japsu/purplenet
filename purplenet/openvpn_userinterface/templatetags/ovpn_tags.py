# encoding: utf-8
# vim: shiftwidth=4 expandtab
#
# PurpleNet - a Web User Interface for OpenVPN
# Copyright (C) 2009  Santtu Pajukanta
# Copyright (C) 2008, 2009  Tuure Vartiainen, Antti Niemelä, Vesa Salo
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
The ovpn_tags tag library for Django Templates. Implements several template
tags used across the templates.
"""

from django import template
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.template.loader import render_to_string

from purplenet.openvpn_userinterface.models import Client, Org, AdminGroup

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
    elif isinstance(group_or_org, AdminGroup):
        admin_group = group_or_org
        return reverse("remove_client_from_admin_group_page", kwargs=dict(
            client_id=_get_client_id(user),
            admin_group_id=admin_group.id
        ))
    else:
        raise AssertionError("remove_client_link called with something else than Org or AdminGroup")

@register.simple_tag
def trivial_form(form, post_url="", submit_text="Save"):
    return render_to_string("openvpn_userinterface/trivial_form.html", {
        "form" : form,
        "post_url" : post_url,
        "submit_text" : submit_text,    
    })

@register.simple_tag
def manage_link(obj, client_or_user):
    if isinstance(client_or_user, User):
        client = Client.objects.get(user=client_or_user)
    else:
        client = client_or_user
    
    if obj.may_be_managed_by(client):
        return u'<a href="%s">%s</a>' % (obj.manage_url, obj.name)
    else:
        return obj.name

@register.simple_tag
def media_path():
    return settings.MEDIA_URL
