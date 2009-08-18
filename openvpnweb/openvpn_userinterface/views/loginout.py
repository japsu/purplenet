# encoding: utf-8
# vim: shiftwidth=4 expandtab

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponseNotAllowed
from django.contrib.auth import authenticate, login, logout
from django.core.urlresolvers import reverse
from django.conf import settings

from openvpnweb.openvpn_userinterface.models import Client
from openvpnweb.openvpn_userinterface.access_control import update_group_membership

from .helpers import post_confirmation_page
from ..logging import log

def login_page(request):
    vars = {
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
            client = None
            try:
                client = Client.objects.get(user=user)
            except Client.DoesNotExist:
                client = Client(user=user)
                client.save()

            if settings.OPENVPNWEB_USE_GROUP_MAPPINGS:
                update_group_membership(client)

            request.session["client"] = client
            
            return HttpResponseRedirect(reverse("main_page"))
        else:
            vars = RequestContext(request, {
               'type' : "error", 
               'message_login' : "Your login details are incorrect or " +
                    "your account has been disabled. Please try again."
            })
                          
    return render_to_response('openvpn_userinterface/login.html', vars,
        context_instance=context)
                
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

