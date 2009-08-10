# encoding: utf-8
# vim: shiftwidth=4 expandtab

from django.core.urlresolvers import reverse
from django.http import (HttpResponseRedirect, HttpResponseForbidden,
    HttpResponseNotAllowed)
from django.shortcuts import render_to_response
from django.template import RequestContext

from datetime import datetime, timedelta

from openvpnweb.openvpn_userinterface.forms import SetupForm
from openvpnweb.openvpn_userinterface.models import (IntermediateCA, ServerCA,
    CACertificate)

import os

def create_ca(common_name, ca, base_dir, ca_cls):
    # XXX
    now = datetime.now()
    then = now + timedelta(days=3650)

    sanitized_common_name = "".join(i for i in common_name
        if i.isalpha() or i in "._-").lower()
    dir = os.path.join(base_dir, sanitized_common_name)

    new_ca_cert = CACertificate(
        common_name=common_name,
        ca=ca,
        granted=now,
        expires=then
    )
    new_ca = ca_cls(
        dir=dir,
        owner=None,
        certificate=new_ca_cert
    )

    new_ca.create_ca()
    new_ca_cert.save()
    new_ca.save()

    return new_ca

def setup_page(request):
    if request.method == "GET":
        form = SetupForm()

        vars = {
            "form" : form,
        }
        
        return render_to_response("openvpn_userinterface/setup.html", vars,
            context_instance=RequestContext(request, {}))

    elif request.method == "POST":
        form = SetupForm(request.POST)

        if form.is_valid():
            # CREATE THE CA HIERARCHY
        
            base_dir = form.cleaned_data["ca_dir"]

            # Root CA
            root_ca = create_ca(
                form.cleaned_data["root_ca_cn"],
                None,
                base_dir,
                IntermediateCA
            )

            # Server CA
            server_ca = create_ca(
                form.cleaned_data["server_ca_cn"],
                root_ca,
                base_dir,
                ServerCA
            )

            # Client CA
            client_ca = create_ca(
                form.cleaned_data["client_ca_cn"],
                root_ca,
                base_dir,
                IntermediateCA
            )

            return HttpResponseRedirect(reverse("login_page"))

        else:
            vars = {
                "form" : form,
            }
            return render_to_response("openvpn_userinterface/setup.html", vars,
                context_instance=RequestContext(request, {}))

    else:
        return HttpResponseNotAllowed(["GET", "POST"])
