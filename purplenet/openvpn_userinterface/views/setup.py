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
The standalone and Shibboleth setup views.
"""

from django.core.urlresolvers import reverse
from django.http import (HttpResponseRedirect, HttpResponseForbidden,
    HttpResponseNotAllowed)
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.models import User, Group
from django.conf import settings

from datetime import datetime, timedelta

from ..forms import StandaloneSetupForm, ShibbolethSetupForm
from ..models import (IntermediateCA, ServerCA, CACertificate, Client,
    SiteConfig, AdminGroup, load_org_map, validate_org_map)
from ..access_control import require_standalone, require_shibboleth
from .helpers import create_view, redirect
from libpurplenet.helpers import mkdir_check

import os

def create_ca(common_name, ca, ca_cls):
    # XXX
    now = datetime.now()
    then = now + timedelta(days=3650)
    
    base_dir = SiteConfig.objects.get().ca_base_dir

    sanitized_common_name = "".join(i for i in common_name
        if i.isalpha() or i in "._-").lower()

    new_ca_cert = CACertificate(
        common_name=common_name,
        ca=ca,
        granted=now,
        expires=then
    )
    new_ca_cert.save()
    
    new_ca = ca_cls(
        dir_name=sanitized_common_name,
        owner=None,
        certificate=new_ca_cert
    )

    new_ca.create_ca()
    new_ca.save()

    return new_ca

def _common_setup(request, form):
    if SiteConfig.objects.all():
        return HttpResponseForbidden()

    base_dir = form.cleaned_data["ca_dir"]
    
    copies_dir = os.path.join(base_dir, "copies")
    mkdir_check(copies_dir, False)

    # CREATE THE SUPERUSER GROUP AND ACCOUNT

    
    supergroup = Group(name="Superusers")
    supergroup.save()
    superadm = AdminGroup(group=supergroup)
    superadm.save()
    
    # CREATE THE SITE CONFIG
    siteconfig = SiteConfig(
        superuser_group=supergroup,
        ca_base_dir=base_dir
    )
    siteconfig.save()
    
    # CREATE THE CA HIERARCHY

    # Root CA
    root_ca = create_ca(
        form.cleaned_data["root_ca_cn"],
        None,
        IntermediateCA
    )

    # Server CA
    server_ca = create_ca(
        form.cleaned_data["server_ca_cn"],
        root_ca,
        ServerCA
    )

    # Client CA
    client_ca = create_ca(
        form.cleaned_data["client_ca_cn"],
        root_ca,
        IntermediateCA
    )
    
    siteconfig.root_ca=root_ca
    siteconfig.server_ca=server_ca
    siteconfig.client_ca=client_ca
    siteconfig.save()

@require_standalone
@create_view(StandaloneSetupForm, "openvpn_userinterface/setup.html")
def _standalone_setup_page(request, form):
    _common_setup(request, form)
    
    siteconfig = SiteConfig.objects.get()
    
    superuser = User(username=form.cleaned_data["superuser_name"])
    superuser.set_password(form.cleaned_data["password"])
    superuser.save()
    
    superclient = Client(user=superuser)
    superclient.save()
    
    siteconfig.superuser_group.user_set.add(superuser)
    
    return redirect("setup_complete_page")
    
@require_shibboleth
@create_view(ShibbolethSetupForm, "openvpn_userinterface/setup.html")
def _shibboleth_setup_page(request, form):
    _common_setup(request, form)
    
    load_org_map(form.cleaned_data["org_map"])
    
    return redirect("setup_complete_page")
    
def setup_page(*args, **kwargs):
    if settings.PURPLENET_USE_SHIBBOLETH:
        return _shibboleth_setup_page(*args, **kwargs)
    else:
        return _standalone_setup_page(*args, **kwargs)
