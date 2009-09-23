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

"""helpers.py - Generic helper views

This module provides helpful generic views and view decorators.,
"""

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseNotAllowed, HttpResponseRedirect
from django.views.decorators.http import require_http_methods
from django.core.urlresolvers import reverse

from functools import wraps

def post_confirmation_page(request, question, choices):
    """post_confirmation_page(request, question, choices) -> response

    A helper for implementing the lo-REST protocol. Should a POST-only resource
    be accessed with the GET method, this method may be used to return a
    confirmation page that allows the user to retry with the POST method or
    cancel.
    """

    client = request.session.get("client", None)

    vars = RequestContext(request, {
        "question" : question,
        "choices" : choices,
        "client" : client,
    })
    return render_to_response("openvpn_userinterface/confirmation.html", vars)

def create_view(form_class, template):
    """@create_view(form_class, template, vars={}) def my_func(request, form)
    
    Assuming that my_func implements the logic to handle a valid form of the
    form_class class, create_view decorates my_func with the logic to render
    the specified template on a GET request and to handle form data on a POST
    request and re-render the template if there are errors in the form. The
    function my_func only gets called when the request method is POST and the
    form is completed successfully (that is, form.is_valid() == True).
    
    The view created using this decorator takes by default no other arguments
    than request. If extra parameters are passed to the view as either
    positional or keyword arguments, they are passed to my_func unaltered.
    
    The template specified by template_name is provided a RequestContext with
    two extra variables: form, that contains the instance of form_class, and
    client, that contains, well, request.session.get("client"). The vars
    dictionary is also imported into the context.
    
    my_func should do whatever processing is required to handle the form data
    and return an HttpResponse instance - preferably an HttpResponseRedirect
    to some view that tells the user he's done a great job.
    
    Requests other than GET or POST are met with extreme prejudice (that is,
    405 Method Not Allowed).
    
    Please keep access control decorators outer than create_view so that
    access violations get caught at an early stage.
    
    If you find all this difficult to understand, just imagine the code of,
    say, purplenet.openvpn_userinterface.views.manage.create_org_page copied
    and pasted at the line reading
    
        return func(request, form)
    
    and Use the Source, Luke.
    """
    def __outer(func):
        @wraps(func)
        @require_http_methods(["GET","POST"])
        def __inner(request, *args, **kwargs):
            client = request.session.get("client")
            vars = dict(client=client)
            context = RequestContext(request, {})
            
            if request.method == "GET":
                form = form_class()
                vars["form"] = form
                
                # fall_through
            
            else: # request.method == "POST"
                form = form_class(request.POST)
                vars["form"] = form
                
                if form.is_valid():
                    return func(request, form, *args, **kwargs)
                else:
                    # Errors in the form
                    # Fall through
                    pass
            
            return render_to_response(template, vars,
                context_instance=context)
        
        return __inner
    return __outer

def redirect(view_name, **kwargs):
    return HttpResponseRedirect(reverse(view_name, kwargs=kwargs))