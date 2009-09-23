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
Logging facilities for the OpenVPN user interface. Contains the LogEntry
model and related functions.
"""

from django.db import models
from django.contrib.auth.models import Group

class LogEntry(models.Model):
    timestamp = models.DateTimeField(auto_now=True)

    EVENT_CHOICES = [
        ("org_map.client_added_to_group", "User mapped into a group"),
        ("org_map.client_removed_from_group", "User de-mapped from a group"),
        ("client_certificate.create", "Client certificate created"),
        ("client_certificate.revoke", "Client certificate revoked"),
    ]
    event = models.CharField(max_length=50, choices=EVENT_CHOICES)

    denied = models.BooleanField(default=False)
    client = models.ForeignKey("Client")
    group = models.ForeignKey(Group, related_name="log_entry_set")

    client_certificate = models.ForeignKey("ClientCertificate", null=True,
        blank=True, related_name="log_entry_set")
    network = models.ForeignKey("Network", null=True, blank=True,
        related_name="log_entry_set")

    class Meta:
        app_label = "openvpn_userinterface"
