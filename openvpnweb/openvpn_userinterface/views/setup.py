# encoding: utf-8
# vim: shiftwidth=4 expandtab

from django.core.urlresolvers import reverse
from django.http import (HttpResponseRedirect, HttpResponseForbidden,
    HttpResponseNotAllowed)
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.models import User, Group

from datetime import datetime, timedelta

from ..forms import SetupForm
from ..models import (IntermediateCA, ServerCA, CACertificate, Client,
    SiteConfig)
from .helpers import create_view

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

@create_view(SetupForm, "openvpn_userinterface/setup.html")
def setup_page(request, form):
    if SiteConfig.objects.all():
        return error_page(request, "The setup process has already been completed.")
    
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
    
    # CREATE THE SUPERUSER GROUP AND ACCOUNT
    superuser = User(username=form.cleaned_data["superuser_name"])
    superuser.set_password(form.cleaned_data["password"])
    superuser.save()
    
    supergroup = superuser.groups.create(name="Superusers")
    
    superclient = Client(user=superuser)
    superclient.save()
    
    # CREATE THE SITE CONFIG
    siteconfig = SiteConfig(
        superuser_group=supergroup,
        root_ca=root_ca,
        server_ca=server_ca,
        client_ca=client_ca
    )
    siteconfig.save()

    return HttpResponseRedirect(reverse("setup_complete_page"))
