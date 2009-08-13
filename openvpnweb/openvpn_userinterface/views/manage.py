# encoding: utf-8
# vim: shiftwidth=4 expandtab

from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.conf import settings
from django.contrib.auth.models import Group, User

from openvpnweb.access_control import manager_required
from openvpnweb.openvpn_userinterface.models import (ClientCertificate, Org,
    Network, Client, Server)

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

def manage_group_page(request, group_id):
    group = get_object_or_404(Group, id=int(group_id))
    org = get_object_or_404(Org, group=group)
    
    return HttpResponseRedirect(reverse("manage_org_page", org_id=org.id))

# XXX The following are stubs

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
def remove_client_from_group_page(request, client_id, group_id):
    client = get_object_or_404(Client, id=int(client_id))
    group = get_object_or_404(Group, id=int(group_id))