# coding: utf-8
# vim: shiftwidth=4 expandtab

from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import (user_passes_test, 
    REDIRECT_FIELD_NAME)
from django.conf import settings

from openvpnweb.openvpn_userinterface.models import *

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

# TODO O(n) for n of MappingElement (may be in thousands). Should there be
# a performance problem, start reusing MappingElements and build a tree of
# them. Or something.
#
# Another approach would be to register all interesting source names
# somewhere, get their values unconditionally and then search the database
# for matching mappings.
def update_group_membership(client):
    mappings = OrgMapping.objects.all()
    orgs = []
    for mapping in mappings:
        if all(elem.matches(client) for elem in mapping.element_set.all()):
            orgs.append(mapping.org)
    groups = Group.objects.filter(org__in=orgs)
    client.user.groups = groups
