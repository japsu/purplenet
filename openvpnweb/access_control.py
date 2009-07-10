# coding: utf-8
# vim: shiftwidth=4 expandtab

from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import (user_passes_test, 
    REDIRECT_FIELD_NAME)

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
        

