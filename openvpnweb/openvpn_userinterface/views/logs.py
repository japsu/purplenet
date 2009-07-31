# encoding: utf-8
# vim: shiftwidth=4 expandtab

from django.shortcuts import render_to_response
from django.template import RequestContext

from openvpnweb.access_control import manager_required
from ..models import LogEntry

@manager_required
def manage_log_page(request):
    client = request.session["client"]
    orgs = client.managed_org_set.all()

    log_entries = LogEntry.objects.filter(org__in=orgs)

    vars = {
        "client" : client,
        "log_entries" : log_entries
    }
    
    return render_to_response("openvpn_userinterface/manage_log.html", vars,
        context_instance=RequestContext(request, {}))
    
