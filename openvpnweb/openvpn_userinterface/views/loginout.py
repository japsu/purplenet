# encoding: utf-8
# vim: shiftwidth=4 expandtab

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponseNotAllowed
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse, resolve, Resolver404
from django.conf import settings
from os import environ

from openvpnweb.openvpn_userinterface.models import Client
from openvpnweb.openvpn_userinterface.access_control import update_group_membership

from .helpers import post_confirmation_page
from ..logging import log

def _standalone_login_page(request):
    vars = {
        "external_auth" : settings.OPENVPNWEB_USE_SHIBBOLETH,
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
        
    # TODO Does next_url need validation?
    next_url = request.GET.get('next', reverse("main_page"))
    return HttpResponseRedirect(next_url)
        

def login_page(*args, **kwargs):
    if settings.OPENVPNWEB_USE_SHIBBOLETH:
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
        return HttpResponseRedirect(reverse("login_page"))
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

