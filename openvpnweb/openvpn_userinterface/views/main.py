# encoding: utf-8
# vim: shiftwidth=4 expandtab

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required

from openvpnweb.openvpn_userinterface.models import ClientCertificate

@login_required
def main_page(request):
    client = request.session["client"]
    
    # XXX try to replace with smarter queries
    data = []
    for org in client.orgs.all():
        networks = []
        for net in org.accessible_network_set.all():
            certificates = ClientCertificate.objects.filter(
                network=net,
                ca__owner__exact=org,
                owner=client
            )
            networks.append((net, certificates))
        data.append((org, networks))

    variables = RequestContext(request, {
        'data': data,
        'client': client,
    })
    
    return render_to_response(
        'openvpn_userinterface/main_page.html', variables 
    )

