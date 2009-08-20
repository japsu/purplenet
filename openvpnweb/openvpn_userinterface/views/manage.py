# encoding: utf-8
# vim: shiftwidth=4 expandtab

from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.conf import settings
from django.contrib.auth.models import Group, User, UNUSABLE_PASSWORD
from django.core.urlresolvers import reverse
from django.http import (HttpResponseForbidden, HttpResponseRedirect,
    HttpResponseNotAllowed)

from ..access_control import manager_required, superuser_required
from ..models import (ClientCertificate, Org, Network, Client, Server,
    SiteConfig, InterestingEnvVar)
from ..forms import (CreateOrgForm, CreateClientForm, ClientSearchForm,
    SelectGroupForm, CreateServerForm, SimpleNetworkForm, CreateGroupForm)
from .helpers import create_view, post_confirmation_page

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
        kwargs=dict(client_id=client.id)))

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
def remove_client_from_group_page(request, client_id, group_id):
    client_to_remove = get_object_or_404(Client, id=int(client_id))
    group = get_object_or_404(Group, id=int(group_id))
    
    if request.method == "POST":
        group.user_set.remove(client_to_remove.user)
        
        return HttpResponseRedirect(reverse("manage_page"))
    
    elif request.method == "GET":
        return post_confirmation_page(request,
            question="Remove %s from %s?" % (
                client_to_remove.user.username,
                group.name
            ),
            choices=[
                ("Remove", reverse("remove_client_from_group_page", kwargs=dict(
                    client_id=client_id,
                    group_id=group_id
                ))),
                ("Cancel", reverse("manage_page"))
            ]
        )
    
    else:
        return HttpResponseNotAllowed(["GET", "POST"])

@manager_required
def remove_client_from_org_page(request, client_id, org_id):
    client = request.session["client"]
    client_to_remove = get_object_or_404(Client, id=int(client_id))
    org = get_object_or_404(Org, id=int(org_id))
    group = org.group
    
    if not client.may_manage(org):
        return HttpResponseForbidden()
    
    if request.method == "POST":
        group.user_set.remove(client_to_remove.user)
        
        return HttpResponseRedirect(reverse("manage_org_page", kwargs=dict(
            org_id=org_id)))
    
    elif request.method == "GET":
        return post_confirmation_page(
            question="Remove %s from %s?" % (
                client_to_remove.user.username,
                group.name
            ),
            choices=[
                ("Remove", reverse("remove_client_from_org_page", kwargs=dict(
                    client_id=client_id,
                    org_id=org_id
                ))),
                ("Cancel", reverse("manage_org_page", kwargs=dict(
                    org_id=org_id
                )))
            ]
        )
    
    else:
        return HttpResponseNotAllowed(["GET", "POST"])

@superuser_required
def remove_admin_group_from_org_page(request, org_id, group_id):
    client = request.session["client"]
    org = get_object_or_404(Org, id=int(org_id))
    group = get_object_or_404(Group, id=int(group_id))
    
    if request.method == "POST":
        org.admin_group_set.remove(group)
        
        return HttpResponseRedirect(reverse("manage_org_page", kwargs=dict(
            org_id=org_id)))
    
    elif request.method == "GET":
        return post_confirmation_page(
            question="Remove %s from the administrators of %s?" % (
                group.name,
                org.name
            ),
            choices=[
                ("Remove", reverse("remove_admin_group_from_org_page", kwargs=dict(
                    org_id=org_id,
                    group_id=group_id,
                ))),
                ("Cancel", reverse("manage_org_page", kwargs=dict(
                    org_id=org_id
                )))
            ]
        )
    
    else:
        return HttpResponseNotAllowed(["GET", "POST"])

# XXX The following are stubs

@superuser_required
@create_view(CreateServerForm, "openvpn_userinterface/create_server.html")
def create_server_page(request):
    pass

@superuser_required
@create_view(SimpleNetworkForm, "openvpn_userinterface/create_server.html")
def create_network_page(request):
    pass

@superuser_required
@create_view(CreateGroupForm, "openvpn_userinterface/create_server.html")
def create_group_page(request):
    pass

@superuser_required
def manage_group_page(request, group_id):
    group = get_object_or_404(Group, id=int(group_id))
    org = get_object_or_404(Org, group=group)
    
    return HttpResponseRedirect(reverse("manage_org_page", org_id=org.id))

@superuser_required
def manage_network_page(request, org_id, net_id):
    org = get_object_or_404(Org, id=int(org_id))
    network = get_object_or_404(Network, id=int(net_id))

@superuser_required
def manage_server_page(request, server_id):
    server = get_object_or_404(Server, id=int(server_id))

@superuser_required
def manage_org_map_page(request):
    pass

@manager_required
def manage_client_page(request, client_id):
    client_to_manage = get_object_or_404(Client, id=int(client_id))
    
