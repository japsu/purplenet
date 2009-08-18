# encoding: utf-8
# vim: shiftwidth=4 expandtab

from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.conf import settings
from django.contrib.auth.models import Group, User, UNUSABLE_PASSWORD
from django.http import (HttpResponseForbidden, HttpResponseRedirect,
    HttpResponseNotAllowed)

from ..access_control import manager_required, superuser_required
from ..models import (ClientCertificate, Org, Network, Client, Server,
    SiteConfig, InterestingEnvVar)
from ..forms import OrgForm, ClientForm
from .helpers import create_view

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

    vars = {
        "org" : org,
        "external_auth" : settings.OPENVPNWEB_USE_GROUP_MAPPINGS
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
@create_view(OrgForm, "openvpn_userinterface/create_org.html")
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
@create_view(ClientForm, "openvpn_userinterface/create_client.html")
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

# XXX The following are stubs

def manage_group_page(request, group_id):
    group = get_object_or_404(Group, id=int(group_id))
    org = get_object_or_404(Org, group=group)
    
    return HttpResponseRedirect(reverse("manage_org_page", org_id=org.id))

@manager_required
def manage_network_page(request, org_id, net_id):
    org = get_object_or_404(Org, id=int(org_id))
    network = get_object_or_404(Network, id=int(net_id))

@manager_required
def manage_server_page(request, server_id):
    server = get_object_or_404(Server, id=int(server_id))

@manager_required
def manage_org_map_page(request):
    pass

@manager_required
def manage_client_page(request, client_id):
    client = get_object_or_404(Client, id=int(client_id))

@manager_required
def add_client_to_group_page(request, client_id, group_id):
    client = get_object_or_404(Client, id=int(client_id))
    group = get_object_or_404(Group, id=int(group_id))    

@manager_required
def remove_client_from_group_page(request, client_id, group_id):
    client = get_object_or_404(Client, id=int(client_id))
    group = get_object_or_404(Group, id=int(group_id))
    
@manager_required
def create_server_page(request):
    pass

@manager_required
def create_network_page(request):
    pass

@manager_required
def create_group_page(request):
    pass