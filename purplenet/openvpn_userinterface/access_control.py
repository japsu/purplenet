# encoding: utf-8
# vim: shiftwidth=4 expandtab
#
# PurpleNet - a Web User Interface for OpenVPN
# Copyright (C) 2009  Santtu Pajukanta
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
Access control decorators and other functions for PurpleNet.
"""

from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import (user_passes_test, 
    REDIRECT_FIELD_NAME)
from django.conf import settings

from purplenet.openvpn_userinterface.models import (Client, InterestingEnvVar,
    MappingElement)
from purplenet.openvpn_userinterface.logging import log

from os import environ
from itertools import groupby
from functools import wraps

def manager_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME):
    """@manager_required(redirect_field_name=REDIRECT_FIELD_NAME)

    Makes this view accessible only to users that have been designated as
    being allowed to manage some organization in the system. Further checks
    need to be done to validate specific management requests."""
    
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated() and Client.objects.get(user=u).may_view_management_pages(),
        redirect_field_name=redirect_field_name
    )

    if function:
        return actual_decorator(function)
    return actual_decorator

def superuser_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME):
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated() and Client.objects.get(user=u).is_superuser,
        redirect_field_name=redirect_field_name
    )
    
    if function:
        return actual_decorator(function)
    return actual_decorator

def update_group_membership(client):
    elements = list()

    for var in InterestingEnvVar.objects.all():
        value = environ.get(var.name, None)
        elements.extend(MappingElement.objects.filter(
            type__namespace__exact="env",
            type__source_name__exact=var.name,
            value=value
        ))

    KEY_FUNC = lambda x: x.mapping
    elements.sort(key=KEY_FUNC)
    grouped = groupby(elements, KEY_FUNC)
    
    new_groups = set()

    for mapping, elements in grouped:
        if list(mapping.element_set.all()) == list(elements):
            new_groups.add(mapping.group)

    old_groups = set(client.user.groups.all())
    client.user.groups = new_groups
    client.save()

    groups_removed = old_groups - new_groups
    groups_added = new_groups - old_groups
    
    for group in groups_removed:
        log(
            event="org_map.client_removed_from_group",
            client=client,
            group=group
        )

    for group in groups_added:
        log(
            event="org_map.client_added_to_group",
            client=client,
            group=group
        )

def require_shibboleth(func):
    """@require_shibboleth def ...
    
    Prevents the decorated view from being used when the application is not
    installed in Shibboleth mode.
    """
    @wraps(func)
    def _inner(*args, **kwargs):
        if not settings.PURPLENET_USE_SHIBBOLETH:
            return HttpResponseForbidden()
        else:
            return func(*args, **kwargs)
    
    return _inner

def require_standalone(func):
    """@require_shibboleth def ...
    
    Prevents the decorated view from being used when the application is not
    installed in standalone (ie. non-Shibboleth) mode.
    """
    @wraps(func)
    def _inner(*args, **kwargs):
        if settings.PURPLENET_USE_SHIBBOLETH:
            return HttpResponseForbidden()
        else:
            return func(*args, **kwargs)
    
    return _inner
