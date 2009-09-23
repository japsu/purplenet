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
Models related to site configuration.
"""

from django.db import models
from django.contrib.auth.models import Group

import os

class SiteConfig(models.Model):
    superuser_group = models.OneToOneField(Group)
    
    root_ca = models.OneToOneField("IntermediateCA", related_name="int_scfg_rca", null=True, blank=True)
    server_ca = models.OneToOneField("ServerCA", related_name="int_scfg_sca", null=True, blank=True)
    client_ca = models.OneToOneField("IntermediateCA", related_name="int_scfg_cca", null=True, blank=True)
    
    ca_base_dir = models.CharField(max_length=200)
    
    @property
    def copies_dir(self):
        return os.path.join(self.ca_base_dir, "copies")
    
    class Meta:
        app_label = "openvpn_userinterface"
        
class InterestingEnvVar(models.Model):
    name = models.CharField(max_length=200)
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        app_label = "openvpn_userinterface"