# encoding: utf-8
# vim: shiftwidth=4 expandtab

from ..access_control import manager_required, superuser_required
from ..forms import (CreateOrgForm, CreateClientForm, ClientSearchForm,
    SelectGroupForm, ServerForm, NetworkForm, CreateGroupForm,
    SelectNetworkForm, SelectServerForm, ClientForm, ProfileForm,
    SelectProfileForm)
from ..models import (ClientCertificate, Org, Network, Client, Server, SiteConfig,
    InterestingEnvVar, ServerCertificate, NetworkProfile, ProfileInheritance)
from .helpers import create_view, post_confirmation_page
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth.models import Group, User, UNUSABLE_PASSWORD
from django.core.urlresolvers import reverse
from django.http import (HttpResponseForbidden, HttpResponseRedirect,
    HttpResponseNotAllowed)
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.views.decorators.http import require_POST, require_http_methods

# TODO: Split into smaller files

@manager_required
def manage_page(request):
    client = request.session["client"]

    data = list()
    for org in client.managed_org_set.all():
        networks = []
        for net in org.accessible_network_set.all():
            certificates = ClientCertificate.objects.filter(
                network=net,
                ca__owner__exact=org
            ).order_by('owner__user__username')
            networks.append((net, certificates))
        data.append((org, networks))

    vars = RequestContext(request, {
        "external_auth" : settings.OPENVPNWEB_USE_GROUP_MAPPINGS,
        "client" : client,
        "data" : data,
    })
    return render_to_response("openvpn_userinterface/manage.html", vars)

@manager_required
def manage_org_page(request, org_id):
    org = get_object_or_404(Org, id=int(org_id))
    client = request.session["client"]
    
    if not client.may_manage(org):
        return HttpResponseForbidden()

    vars = {
        "client" : client,
        "org" : org,
        "external_auth" : settings.OPENVPNWEB_USE_GROUP_MAPPINGS,
    }
    context = RequestContext(request, {})

    if request.method == "POST":
        # XXX Do something.
        pass
    
    elif request.method == "GET":
        return render_to_response("openvpn_userinterface/manage_org.html",
            vars, context_instance=context)
    
    else:
        return HttpResponseNotAllowed(["GET","POST"])            

@superuser_required
@create_view(CreateOrgForm, "openvpn_userinterface/create_org.html")
def create_org_page(request, form):
    user_group = Group(name=form.cleaned_data["name"])
    user_group.save()
    
    org = Org(
        group=user_group,
        cn_suffix=form.cleaned_data["cn_suffix"]
    )
    org.save()
    
    return HttpResponseRedirect(reverse("manage_org_page",
        kwargs=dict(org_id=org.id)))


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

@superuser_required
@create_view(ClientSearchForm, "openvpn_userinterface/add_client_to_group.html")
def add_client_to_group_page(request, form, group_id):
    group = get_object_or_404(Group, id=int(group_id))
    client_to_add = form.search_result
    
    group.user_set.add(client_to_add.user)
    
    return HttpResponseRedirect(reverse("manage_page"))

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
@create_view(SelectGroupForm,
    "openvpn_userinterface/add_admin_group_to_org.html")
def add_admin_group_to_org_page(request, form, org_id):
    org = get_object_or_404(Org, id=int(org_id))
    group_to_add = form.cleaned_data["group"]
    
    org.admin_group_set.add(group_to_add)
    
    return HttpResponseRedirect(reverse("manage_org_page", kwargs=dict(
        org_id=org.id)))
    
@superuser_required
@require_POST
def remove_client_from_group_page(request, client_id, group_id):
    client_to_remove = get_object_or_404(Client, id=int(client_id))
    group = get_object_or_404(Group, id=int(group_id))
    
    group.user_set.remove(client_to_remove.user)
    
    return HttpResponseRedirect(reverse("manage_page"))

@manager_required
@require_POST
def remove_client_from_org_page(request, client_id, org_id):
    client = request.session["client"]
    client_to_remove = get_object_or_404(Client, id=int(client_id))
    org = get_object_or_404(Org, id=int(org_id))
    group = org.group
    
    if not client.may_manage(org):
        return HttpResponseForbidden()
    
    group.user_set.remove(client_to_remove.user)
    
    return HttpResponseRedirect(reverse("manage_org_page", kwargs=dict(
        org_id=org_id)))

@superuser_required
@require_POST
def remove_admin_group_from_org_page(request, org_id, group_id):
    client = request.session["client"]
    org = get_object_or_404(Org, id=int(org_id))
    group = get_object_or_404(Group, id=int(group_id))
    
    org.admin_group_set.remove(group)
    
    return HttpResponseRedirect(reverse("manage_org_page", kwargs=dict(
        org_id=org_id)))
    
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
@require_http_methods(["GET","POST"])
def manage_client_page(request, client_id):
    client = request.session["client"]
    target = get_object_or_404(Client, id=int(client_id))

    orgs = []
    managed_orgs = client.managed_org_set
    
    for org in target.orgs:
        orgs.append((org, org in managed_orgs))

    if request.method == "POST":
        form = ClientForm(request.POST, instance=target)
        
        if form.is_valid():
            user = client.user
            
            user.username = form.cleaned_data["username"]
            user.first_name = form.cleaned_data["first_name"]
            user.last_name = form.cleaned_data["last_name"]
            
            user.save()
    else:
        form = Clientform(instance=target)

    context = RequestContext(request, {})
    vars = {
        "form" : form,
        "orgs" : orgs,
        "client" : client,
        "target" : target,
        "external_auth" : settings.OPENVPNWEB_USE_GROUP_MAPPINGS,
    }
    
    return render_to_response("openvpn_userinterface/manage_client.html",
        vars, context_instance=context)

@superuser_required
@create_view(SelectServerForm, "openvpn_userinterface/add_server_to_network.html")
def add_server_to_network_page(request, form, network_id):
    network = get_object_or_404(Network, id=int(network_id))
    server = form.cleaned_data["server"]
    
    network.server_set.add(server)
    
    return HttpResponseRedirect(reverse("manage_network_page",
        kwargs={"network_id":network_id}))

@superuser_required
@create_view(SelectNetworkForm, "openvpn_userinterface/add_network_to_server.html")
def add_network_to_server_page(request, form, server_id):
    server = get_object_or_404(Server, id=int(server_id))
    network = form.cleaned_dat["network"]
    
    server.network_set.add(network)
    
    return HttpResponseRedirect(reverse("manage_server_page",
        kwargs={"server_id":server_id}))
    
@superuser_required
@require_POST
def remove_network_from_server_page(request, form, server_id, network_id):
    network = get_object_or_404(Network, id=int(network_id))
    server = get_object_or_404(Server, id=int(server_id))
    
    server.network_set.remove(network)
    return HttpResponseRedirect(reverse("manage_server_page",
        kwargs={"server_id":server_id}))

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
    cert.create_files()
    
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
@create_view(CreateGroupForm, "openvpn_userinterface/create_server.html")
def create_group_page(request, form):
    group = form.save()
    
    return HttpResponseRedirect(reverse("manage_group_page",
        kwargs={"group_id":group.id}))

@superuser_required
def manage_group_page(request, group_id):
    client = request.session["client"]
    group = get_object_or_404(Group, id=int(group_id))

    vars = {
        "client" : client,
        "group" : group,
    }
    context = RequestContext(request, {})
    
    return render_to_response("openvpn_userinterface/manage_group.html",
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
@require_http_methods(["GET","POST"])
def manage_profile_page(request, profile_id):
    client = request.session["client"]
    profile = get_object_or_404(NetworkProfile, id=int(profile_id))

    if request.method == "POST":
        form = ProfileForm(request.POST, instance=profile)
        
        if form.is_valid():
            form.save()
    else:
        form = ProfileForm(instance=profile)
    
    vars = {
        "form" : form,
        "profile" : profile,
        "client" : client,
    }
    context = RequestContext(request, {})
    
    return render_to_response("openvpn_userinterface/manage_profile.html",
        vars, context_instance=context)

# XXX The following are stubs

@superuser_required
def manage_org_map_page(request):
    pass
    
