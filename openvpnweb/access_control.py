# coding: utf-8
# vim: shiftwidth=4 expandtab

from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import (user_passes_test, 
    REDIRECT_FIELD_NAME)
from django.conf import settings

from openvpnweb.openvpn_userinterface.models import *
from openvpnweb.openvpn_userinterface.logging import log

from os import environ
from itertools import groupby

def manager_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME):
    """@manager_required(redirect_field_name=REDIRECT_FIELD_NAME)

    Makes this view accessible only to users that have been designated as
    being allowed to manage some organization in the system. Further checks
    need to be done to validate specific management requests."""
    
    actual_decorator = user_passes_test(
        lambda u: Client.objects.get(user=u).may_view_management_pages(),
        redirect_field_name=REDIRECT_FIELD_NAME
    )

    if function:
        return actual_decorator(function)
    return actual_decorator

def update_group_membership(client):
    # XXX
    INTERESTING_ENVVARS = ["departmentNumber"]
    elements = list()

    for var_name in INTERESTING_ENVVARS:
        value = environ.get(var_name, None)
        elements.extend(MappingElement.objects.filter(
            type__namespace__exact="env",
            type__source_name__exact=var_name,
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
