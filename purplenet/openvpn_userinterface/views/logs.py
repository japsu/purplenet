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
The log viewer.
"""

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.db.models import Q
from django.contrib.auth.models import Group

from ..access_control import manager_required
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
    
