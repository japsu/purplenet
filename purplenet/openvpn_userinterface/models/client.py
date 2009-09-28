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
Contains the Client model.
"""

from django.db import models
from django.contrib.auth.models import User, Group
from purplenet.openvpn_userinterface.models.org import Org, AdminGroup
from purplenet.openvpn_userinterface.models.siteconfig import SiteConfig
from purplenet.openvpn_userinterface.models.certificates import ClientCertificate
from libpurplenet.helpers import sanitize_name

class Client(models.Model):
    user = models.OneToOneField(User)

    @property
    def name(self):
        return self.user.username

    @property
    def sanitized_name(self):
        return sanitize_name(self.name) 

    @property
    def orgs(self):
        return self.org_set
    
    @property
    def org_set(self):
        return Org.objects.filter(group__in=self.user.groups.all())

    @property
    def managed_org_set(self):
        if self.is_superuser:
            return Org.objects.all()
        else:
            return Org.objects.filter(
                admin_group_set__group__in=self.user.groups.all())
    
    @property
    def admin_group_set(self):
        return AdminGroup.objects.filter(group__in=self.user.groups.all())
        
    @property
    def is_superuser(self):
        superuser_group = SiteConfig.objects.get().superuser_group
        return superuser_group in self.user.groups.all()

    def __unicode__(self):
        return self.name

    def may_access(self, org, net):
        return org in self.orgs and org.may_access(net)

    def may_revoke(self, certificate):
        return certificate.owner == self or \
            self.may_manage(certificate.ca.org)

    def may_manage(self, org_or_group):
        if isinstance(org_or_group, Group):
            group = org_or_group
            
            try:
                # user group
                org = Org.objects.get(group=group)
                return self.may_manage(org)
            except:
                # admin or other group
                return self.is_superuser()
        else:
            if self.is_superuser:
                return True
            
            # assume Org
            org = org_or_group
            
            groups = set(ag.group for ag in org.admin_group_set.all())
            return bool(groups.intersection(self.user.groups.all()))
            
    def may_view_management_pages(self):
        return self.is_superuser or bool(self.managed_org_set)

    def get_certificates(self):
        data = []
        for org in self.orgs.all():
            networks = []
            for net in org.accessible_network_set.all():
                certificates = ClientCertificate.objects.filter(
                    network=net,
                    ca__owner__exact=org,
                    owner=self
                ).order_by("granted")
                networks.append((net, certificates))
            data.append((org, org.may_be_managed_by(self), networks))
        
        return data

    class Admin: pass

    class Meta:
        app_label = "openvpn_userinterface"

