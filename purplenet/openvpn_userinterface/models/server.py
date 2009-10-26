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
The Server model.
"""

from django.db import models
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse

from libpurplenet.helpers import sanitize_name

class Server(models.Model):
    name = models.CharField(max_length=30)
    address = models.IPAddressField()
    port = models.IntegerField(max_length=10)
    PROTOCOL_CHOICES = (
        ('tcp','TCP'),
        ('udp','UDP')
    )
    MODE_CHOICES = (
        ('bridged','BRIDGED'),
        ('routed','ROUTED')
    )
    protocol = models.CharField(max_length=30, choices=PROTOCOL_CHOICES)
    mode = models.CharField(max_length=30, choices=MODE_CHOICES) 
    certificate = models.OneToOneField("ServerCertificate",
        related_name="user")

    # REVERSE: network_set = ManyToMany(Network)
    
    EXPORT_FIELDS = ["name", "address", "port", "protocol"]
             
    @property
    def _config_vars(self):
        vars = dict()
        
        # Export some fields to the configuration
        for field_name in Server.EXPORT_FIELDS:
            vars[field_name] = getattr(self, field_name)
        
        # Expand mode to niftier variables
        if self.mode == "bridged":
            vars["bridged"] = True
            vars["routed"] = False
            vars["tun_tap"] = "tap"
        elif self.mode == "routed":
            vars["bridged"] = False
            vars["routed"] = True
            vars["tun_tap"] = "tun"
        else:
            raise AssertionError("mode not in ('bridged', 'routed')")
    
        return vars
    
    @property
    def server_config(self):
        return render_to_string("openvpn_conf/server.conf", self._config_vars)
    
    def __unicode__(self):
        return self.name
    
    def may_be_managed_by(self, client):
        return client.is_superuser
    
    @property
    def manage_url(self):
        return reverse("manage_server_page", kwargs={"server_id":self.id})

    @property
    def sanitized_name(self):
        return sanitize_name(self.name)

    class Admin: pass

    class Meta:
        app_label = "openvpn_userinterface"

