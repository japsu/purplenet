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
Login and logout views.
"""

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponseNotAllowed
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse, resolve, Resolver404
from django.conf import settings
from os import environ

from purplenet.openvpn_userinterface.models import Client
from purplenet.openvpn_userinterface.access_control import update_group_membership

from .helpers import post_confirmation_page, redirect
from ..logging import log

def _standalone_login_page(request):
    vars = {
        "external_auth" : settings.PURPLENET_USE_SHIBBOLETH,
        'type': "info", 
        'message_login': ""
    }
    context = RequestContext(request, {})

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)

        if user is not None and user.is_active:
            login(request, user)    

            client, created = Client.objects.get_or_create(user=user)
            request.session["client"] = client
            
            # TODO Does next_url need validation?
            next_url = request.GET.get('next', reverse("main_page"))
            return HttpResponseRedirect(next_url)
        else:
            vars = RequestContext(request, {
               'type' : "error", 
               'message_login' : "Your login details are incorrect or " +
                    "your account has been disabled. Please try again."
            })
                          
    return render_to_response('openvpn_userinterface/login.html', vars,
        context_instance=context)

def _shibboleth_login_page(request):
    # Assume Shibboleth authentication has been successfully performed
    # and trust values found in the environment.
    user = authenticate()
    
    if user is None:
        return render_to_response("openvpn_userinterface/shibboleth_login_failed.html")

    login(request, user)
    
    client, created = Client.objects.get_or_create(user=user)
    request.session["client"] = client
    
    update_group_membership(client)
        
    # TODO Does next_url need validation?
    next_url = request.GET.get('next', reverse("main_page"))
    return HttpResponseRedirect(next_url)
        

def login_page(*args, **kwargs):
    if settings.PURPLENET_USE_SHIBBOLETH:
        return _shibboleth_login_page(*args, **kwargs)
    else:
        return _standalone_login_page(*args, **kwargs)
                
def logout_page(request):
    if request.method == "POST":
        try:
            del request.session["client"]
        except KeyError, e:
            pass
        
        logout(request)
        
        if settings.PURPLENET_LOGOUT_URL:
            return HttpResponseRedirect(settings.PURPLENET_LOGOUT_URL)
        else:
            return redirect("login_page")
    elif request.method == "GET":
        return post_confirmation_page(request,
            question="Really log out?",
            choices=[
                ("Log out", reverse("logout_page")),
                ("Cancel", reverse("main_page"))
            ]
        )

    else:
        return HttpResponseNotAllowed()

