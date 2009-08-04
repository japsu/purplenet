# encoding: utf-8
# vim: shiftwidth=4 expandtab

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.db.models import Q
from django.contrib.auth.models import Group

from openvpnweb.access_control import manager_required
from ..models import LogEntry

@manager_required
def manage_log_page(request):
    client = request.session["client"]
    orgs = client.managed_org_set.all()

    user_groups = Group.objects.filter(org__in=orgs)
    admin_groups = Group.objects.filter(managed_org_set__in=orgs)

    log_entries = LogEntry.objects.filter(Q(group__in=user_groups) | Q(group__in=admin_groups)).order_by('timestamp')

    vars = {
        "client" : client,
        "log_entries" : log_entries
    }
    
    return render_to_response("openvpn_userinterface/manage_log.html", vars,
        context_instance=RequestContext(request, {}))
    
