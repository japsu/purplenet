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
The management interface of PurpleNet.
"""

from __future__ import with_statement

from ..access_control import (manager_required, superuser_required,
    require_standalone, require_shibboleth)
from purplenet.openvpn_userinterface.forms import *
from purplenet.openvpn_userinterface.models import *
from .helpers import create_view, post_confirmation_page, redirect
from .setup import create_ca
from libpurplenet.helpers import zip_write_file, read_file
from libpurplenet import openssl
from contextlib import closing

import zipfile

from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth.models import Group, User, UNUSABLE_PASSWORD
from django.core.urlresolvers import reverse
from django.http import (HttpResponseForbidden, HttpResponseRedirect,
    HttpResponseNotAllowed, HttpResponse)
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.views.decorators.http import (require_POST, require_http_methods,
    require_GET)

# TODO: Split into smaller files

@manager_required
def manage_page(request):
    client = request.session["client"]

    orgs = client.managed_org_set.all()

    context = RequestContext(request, {})
    vars = {
        "external_auth" : settings.PURPLENET_USE_SHIBBOLETH,
        "client" : client,
    }
    
    if client.is_superuser:
        vars.update(
            all_orgs=Org.objects.all(),
            all_networks=Network.objects.all(),
            all_admin_groups=AdminGroup.objects.all(),
            all_servers=Server.objects.all()
        )
    
    return render_to_response("openvpn_userinterface/manage.html", vars,
        context_instance=context)

NUM_REVOKED=5

@manager_required
@require_GET
def manage_org_page(request, org_id, show_revoked=False):
    org = get_object_or_404(Org, id=int(org_id))
    client = request.session["client"]
    
    if not client.may_manage(org):
        return HttpResponseForbidden()

    networks = []
    
    for network in org.accessible_network_set.all():
        # TODO encapsulate this query as a function somewhere
        certificates = ClientCertificate.objects.filter(
            ca__owner__exact=org,
            network=network
        )
        
        active_certificates = certificates.filter(revoked__isnull=True).order_by("granted")
        all_revoked_certificates = certificates.filter(revoked__isnull=False).order_by("-revoked")
        
        if show_revoked:
            revoked_certificates = all_revoked_certificates
            more_revoked_certificates = False
        else:
            revoked_certificates = all_revoked_certificates[0:NUM_REVOKED].reverse()
            more_revoked_certificates = all_revoked_certificates.count() > NUM_REVOKED
        
        networks.append((network, active_certificates, revoked_certificates, more_revoked_certificates))

    vars = {
        "client" : client,
        "networks" : networks,
        "org" : org,
        "external_auth" : settings.PURPLENET_USE_SHIBBOLETH,
        "num_revoked" : NUM_REVOKED,
    }
    context = RequestContext(request, {})
    
    return render_to_response("openvpn_userinterface/manage_org.html",
        vars, context_instance=context) 

@superuser_required
@create_view(CreateOrgForm, "openvpn_userinterface/create_org.html")
def create_org_page(request, form):
    org_name = form.cleaned_data["name"]
    ca_common_name = org_name # ? 
    
    client_ca = SiteConfig.objects.get().client_ca
    
    user_group = Group(name=ca_common_name)
    user_group.save()
    
    org_ca = create_ca(ca_common_name, client_ca, ClientCA)
    org_ca.save()
    
    org = Org(
        group=user_group,
        cn_suffix=form.cleaned_data["cn_suffix"],
        client_ca=org_ca
    )
    org.save()
    
    org_ca.owner = org
    org_ca.save()
    
    return HttpResponseRedirect(reverse("manage_org_page",
        kwargs=dict(org_id=org.id)))

@require_standalone
@manager_required
@create_view(CreateClientForm, "openvpn_userinterface/create_client.html")
def create_client_page(request, form):
    user = User(
        username=form.cleaned_data["username"],
        first_name=form.cleaned_data["first_name"],
        last_name=form.cleaned_data["last_name"]
    )
    
    password = form.cleaned_data.get("password")
    if password:
        user.set_password(form.cleaned_data["password"])
    else:
        user.password = UNUSABLE_PASSWORD
    user.save()
    
    new_client = Client(user=user)
    new_client.save()
    
    return HttpResponseRedirect(reverse("manage_client_page",
        kwargs=dict(client_id=new_client.id)))

@require_standalone
@superuser_required
@create_view(ClientSearchForm, "openvpn_userinterface/add_client_to_admin_group.html")
def add_client_to_admin_group_page(request, form, admin_group_id):
    admin_group = get_object_or_404(AdminGroup, id=int(admin_group_id))
    client_to_add = form.search_result
    
    admin_group.group.user_set.add(client_to_add.user)
    
    return redirect("manage_admin_group_page", admin_group_id=admin_group_id)

@require_standalone
@manager_required
@create_view(ClientSearchForm, "openvpn_userinterface/add_client_to_org.html")
def add_client_to_org_page(request, form, org_id):
    client = request.session["client"]
    
    org = get_object_or_404(Org, id=int(org_id))
    client_to_add = form.search_result
    
    if not client.may_manage(org):
        return HttpResponseForbidden()
    
    org.group.user_set.add(client_to_add.user)
    
    return HttpResponseRedirect(reverse("manage_org_page", kwargs=dict(
        org_id=org.id)))

@superuser_required
@create_view(SelectAdminGroupForm,
    "openvpn_userinterface/add_admin_group_to_org.html")
def add_admin_group_to_org_page(request, form, org_id):
    org = get_object_or_404(Org, id=int(org_id))
    group_to_add = form.cleaned_data["group"]
    
    org.admin_group_set.add(group_to_add)
    
    return HttpResponseRedirect(reverse("manage_org_page", kwargs=dict(
        org_id=org.id)))

@superuser_required
@create_view(SelectOrgForm,
    "openvpn_userinterface/add_org_to_admin_group.html")
def add_org_to_admin_group_page(request, form, admin_group_id):
    admin_group = get_object_or_404(AdminGroup, id=int(admin_group_id))
    org = form.cleaned_data["org"]

    org.admin_group_set.add(admin_group)

    return redirect("manage_admin_group_page", admin_group_id=admin_group_id)

@require_standalone    
@superuser_required
@require_POST
def remove_client_from_admin_group_page(request, client_id, admin_group_id):
    target = get_object_or_404(Client, id=int(client_id))
    admin_group = get_object_or_404(AdminGroup, id=int(admin_group_id))
    
    admin_group.group.user_set.remove(target.user)
    
    return redirect("manage_admin_group_page", admin_group_id=admin_group_id)

@require_standalone
@manager_required
@require_POST
def remove_client_from_org_page(request, client_id, org_id):
    client = request.session["client"]
    target = get_object_or_404(Client, id=int(client_id))
    org = get_object_or_404(Org, id=int(org_id))
    group = org.group
    
    if not client.may_manage(org):
        return HttpResponseForbidden()
    
    group.user_set.remove(target.user)
    
    return redirect("manage_org_page", org_id=org_id)

@superuser_required
@require_POST
def remove_admin_group_from_org_page(request, org_id, admin_group_id):
    client = request.session["client"]
    org = get_object_or_404(Org, id=int(org_id))
    admin_group = get_object_or_404(AdminGroup, id=int(group_id))
    
    org.admin_group_set.remove(admin_group)
    
    return_url = request.META.get("HTTP_REFERER", reverse(manage_org_page, kwargs={"org_id":org_id}))
    return HttpResponseRedirect(return_url)
    
@superuser_required
@require_POST
def remove_network_from_org_page(request, network_id, org_id):
    client = request.session["client"]
    org = get_object_or_404(Org, id=int(org_id))
    network = get_object_or_404(Network, id=int(network_id))
    
    org.accessible_network_set.remove(network)
    
    # TODO Revoke all existing certificates
    
    return HttpResponseRedirect(reverse("manage_org_page", kwargs=dict(
        org_id=org_id)))

@superuser_required
@create_view(SelectNetworkForm,
    "openvpn_userinterface/add_network_to_org.html")
def add_network_to_org_page(request, form, org_id):
    org = get_object_or_404(Org, id=int(org_id))
    network = form.cleaned_data["network"]
    
    org.accessible_network_set.add(network)
    
    return HttpResponseRedirect(reverse("manage_org_page",
        kwargs=dict(org_id=org_id)))

@manager_required
@require_http_methods(["GET", "POST"])
def manage_client_page(request, client_id):
    client = request.session["client"]
    target = get_object_or_404(Client, id=int(client_id))

    orgs = []
    admin_groups = []
    managed_orgs = client.managed_org_set
    
    for org in target.org_set.all():
        orgs.append((org, org in managed_orgs))
    
    for admin_group in target.admin_group_set.all():
        admin_groups.append((admin_group, admin_group.may_be_managed_by(client)))

    if request.method == "POST":
        form = UserForm(request.POST, instance=target.user)
        
        if form.is_valid():
            form.save()
    else:
        form = UserForm(instance=target.user)

    context = RequestContext(request, {})
    vars = {
        "form" : form,
        "orgs" : orgs,
        "admin_groups" : admin_groups,
        "client" : client,
        "target" : target,
        "external_auth" : settings.PURPLENET_USE_SHIBBOLETH,
    }
    
    return render_to_response("openvpn_userinterface/manage_client.html",
        vars, context_instance=context)

@superuser_required
@create_view(SelectServerForm, "openvpn_userinterface/add_server_to_network.html")
def add_server_to_network_page(request, form, network_id):
    network = get_object_or_404(Network, id=int(network_id))
    server = form.cleaned_data["server"]
    
    network.server_set.add(server)
    
    return redirect("manage_network_page", network_id=network_id)

@superuser_required
@create_view(SelectNetworkForm, "openvpn_userinterface/add_network_to_server.html")
def add_network_to_server_page(request, form, server_id):
    server = get_object_or_404(Server, id=int(server_id))
    network = form.cleaned_data["network"]
    
    server.network_set.add(network)
    
    return redirect("manage_server_page", server_id=server_id)
    
@superuser_required
@require_POST
def remove_network_from_server_page(request, server_id, network_id):
    network = get_object_or_404(Network, id=int(network_id))
    server = get_object_or_404(Server, id=int(server_id))
    
    server.network_set.remove(network)
    return redirect("manage_server_page", server_id=server_id)

@superuser_required
@create_view(ServerForm, "openvpn_userinterface/create_server.html")
def create_server_page(request, form):
    client = request.session["client"]
    server_ca = SiteConfig.objects.get().server_ca
    
    server = form.save(commit=False)
    
    cert = ServerCertificate(
        common_name=form.cleaned_data["name"], # ?
        granted=datetime.now(),
        expires=datetime.now() + timedelta(days=365), # XXX
        ca=server_ca,
        created_by=client
    )
    
    cert.save()
    
    cert.create_certificate()
    cert.save()
    
    server.certificate = cert
    server.save()
    
    return HttpResponseRedirect(reverse("manage_server_page",
        kwargs={"server_id":server.id}))

@superuser_required
@create_view(NetworkForm, "openvpn_userinterface/create_network.html")
def create_network_page(request, form):
    name = form.cleaned_data["name"]
    
    profile = NetworkProfile(name=name)
    profile.save()
    
    network = form.save(commit=False)
    network.profile = profile
    network.save()
    
    return HttpResponseRedirect(reverse("manage_network_page",
        kwargs={"network_id":network.id}))

@superuser_required
@require_http_methods(["GET", "POST"])
def manage_network_page(request, network_id):
    client = request.session["client"]
    network = get_object_or_404(Network, id=int(network_id))
    
    if request.method == "POST":    
        form = NetworkForm(request.POST, instance=network)
        
        if form.is_valid():
            form.save()
    else:
        form = NetworkForm(instance=network)
    
    vars = {
        "form" : form,
        "network" : network,
        "client" : client,
    }
    context = RequestContext(request, {})
    
    return render_to_response("openvpn_userinterface/manage_network.html",
        vars, context_instance=context)

@superuser_required
@create_view(SelectOrgForm, "openvpn_userinterface/add_org_to_network.html")
def add_org_to_network_page(request, form, network_id):
    network = get_object_or_404(Network, id=int(network_id))
    org = form.cleaned_data["org"]
    
    network.orgs_that_have_access_set.add(org)
    
    return redirect("manage_network_page", network_id=network_id)

@superuser_required
@require_http_methods(["GET", "POST"])
def manage_server_page(request, server_id):
    client = request.session["client"]
    server = get_object_or_404(Server, id=int(server_id))
    
    if request.method == "POST":
        form = ServerForm(request.POST, instance=server)
        
        if form.is_valid():
            form.save()
    else:
        form = ServerForm(instance=server)
        
    vars = {
        "server" : server,
        "client" : client,
        "form" : form,
    }
    context = RequestContext(request, {})

    return render_to_response("openvpn_userinterface/manage_server.html",
        vars, context_instance=context)

@superuser_required
@require_GET
def download_server_config_page(request, server_id):
    server = get_object_or_404(Server, id=int(server_id))
    site_config = SiteConfig.objects.get()
    sanitized_name = server.sanitized_name
    
    # TODO encapsulate this
    
    response = HttpResponse(mimetype="application/zip")
    response['Content-Disposition'] = 'filename=%s.zip' % sanitized_name 
    
    server_config = server.server_config
    key = server.certificate.key
    certificate = server.certificate.certificate
    ca_crt_path = site_config.client_ca.get_ca_certificate_path()

    # FIXME
#    pkcs12 = openssl.create_pkcs12(
#        crt=certificate,
#        key=key,
#        chain_dir=site_config.copies_dir,
#        extra_crt_path=ca_crt_path
#    )
    
    with closing(zipfile.ZipFile(response, "w", zipfile.ZIP_DEFLATED)) as zip:
        zip_write_file(zip, "%s.conf" % sanitized_name, server_config, mode=0644)
        zip_write_file(zip, "server.key", key, mode=0400)
        zip_write_file(zip, "server.crt", certificate, mode=0444)
        zip_write_file(zip, "ca.crt", read_file(ca_crt_path), mode=0444)
    
    return response

@superuser_required
@create_view(CreateGroupForm, "openvpn_userinterface/create_admin_group.html")
def create_admin_group_page(request, form):
    group = form.save()
    admin_group = AdminGroup(group=group)
    admin_group.save()
    
    return redirect("manage_admin_group_page", admin_group_id=admin_group.id)

@manager_required
@require_http_methods(["GET","POST"])
def manage_admin_group_page(request, admin_group_id):
    client = request.session["client"]
    admin_group = get_object_or_404(AdminGroup, id=int(admin_group_id))

    orgs = []
    for org in admin_group.managed_org_set.all():
        orgs.append((org, org.may_be_managed_by(client)))

    if request.method == "POST":
        form = CreateGroupForm(request.POST, instance=admin_group.group)
        if form.is_valid():
            form.save()

    else:
        form = CreateGroupForm(instance=admin_group.group)

    vars = {
        "form" : form,
        "orgs" : orgs,
        "client" : client,
        "admin_group" : admin_group,
        "external_auth" : settings.PURPLENET_USE_SHIBBOLETH
    }
    context = RequestContext(request, {})
    
    return render_to_response("openvpn_userinterface/manage_admin_group.html",
        vars, context_instance=context)

@superuser_required
def uninherit_profile_page(request, inheritor_id,
    target_id):
    
    inheritor = get_object_or_404(NetworkProfile, id=int(inheritor_id))
    target = get_object_or_404(NetworkProfile, id=int(target_id))
    
    heirloom = ProfileInheritance.objects.get(
        inheritor=inheritor,
        target=target
    )
    heirloom.delete()
    
    return HttpResponseRedirect(reverse("manage_profile_page",
        kwargs={"profile_id":inheritor_id}))

@superuser_required
@create_view(ProfileForm, "openvpn_userinterface/create_profile.html")
def create_profile_page(request, form):
    profile = form.save()
    
    return HttpResponseRedirect(reverse("manage_profile_page",
        kwargs={"profile_id":profile_id}))

@superuser_required
@create_view(SelectProfileForm, "openvpn_userinterface/inherit_profile.html")
def inherit_profile_page(request, form, inheritor_id):
    inheritor = get_object_or_404(NetworkProfile, id=int(inheritor_id))
    
    target = form.cleaned_data["profile"]
    
    inheritor.inherit(target)
    
    return HttpResponseRedirect(reverse("manage_profile_page",
        kwargs={"profile_id":inheritor_id}))

@superuser_required
@require_http_methods(["GET", "POST"])
def manage_profile_page(request, profile_id):
    client = request.session["client"]
    profile = get_object_or_404(NetworkProfile, id=int(profile_id))

    if request.method == "POST":
        form = ExtendedProfileForm(request.POST)
        
        if form.is_valid():
            profile.name = form.cleaned_data["name"]
            profile.save()
            
            for attr_type in NetworkAttributeType.objects.all():
                value = form.cleaned_data[attr_type.name]
                
                if value:
                    profile.set_attribute(attr_type, value)
                else:
                    profile.clear_attribute(attr_type)
            
    else:
        initial = dict(profile.local_attributes, name=profile.name)
        form = ExtendedProfileForm(initial=initial)
    
    vars = {
        "form" : form,
        "profile" : profile,
        "client" : client,
    }
    context = RequestContext(request, {})
    
    return render_to_response("openvpn_userinterface/manage_profile.html",
        vars, context_instance=context)

@require_standalone
@manager_required
@create_view(SelectOrgForm, "openvpn_userinterface/add_org_to_client.html")
def add_org_to_client_page(request, form, client_id):
    client = request.session["client"]
    target = get_object_or_404(Client, id=int(client_id))
    org = form.cleaned_data["org"]
    
    if not client.may_manage(org):
        # XXX
        return HttpResponseForbidden()
    
    org.group.user_set.add(target.user)
    
    return redirect("manage_client_page", client_id=client_id)

@require_standalone
@manager_required
@create_view(SelectAdminGroupForm, "openvpn_userinterface/add_admin_group_to_client.html")
def add_admin_group_to_client_page(request, form, client_id):
    client = request.session["client"]
    target = get_object_or_404(Client, id=int(client_id))
    admin_group = form.cleaned_data["group"]
    
    if not admin_group.may_be_managed_by(client):
        return HttpResponseForbidden()
    
    admin_group.group.user_set.add(target.user)
    
    return redirect("manage_client_page", client_id=client_id)

@require_shibboleth
@manager_required
@require_http_methods(["GET","POST"])
def manage_org_map_page(request):
    client = request.session["client"]

    vars = dict(client=client)
    context = RequestContext(request, {})

    if client.is_superuser:
        mappings = OrgMapping.objects.order_by("group__name")
        client_groups = Group.objects.all()
    else:
        managed_orgs = client.managed_org_set.all()

        # Select all admin groups to which the client belongs
        client_groups = set(i.group for i in AdminGroup.objects.filter(
            group__in=client.user.groups.all()))
        # Also select all user groups the client manages
        client_groups.update(i.group for i in managed_orgs)

        mappings = OrgMapping.objects.filter(group__in=client_groups).order_by("group__name")
    
    if request.method == "GET":
        form = OrgMapForm(initial={"org_map":dump_org_map(mappings)})
        vars["form"] = form

    else: # POST
        form = OrgMapForm(request.POST)
        vars["form"] = form

        if form.is_valid():
            # Bulldoze old mappings
            for mapping in mappings:
                mapping.delete()
            
            load_org_map(form.cleaned_data["org_map"], restrict_groups=client_groups)
            
            return redirect("manage_page")

    return render_to_response("openvpn_userinterface/manage_org_map.html", vars, context_instance=context)
