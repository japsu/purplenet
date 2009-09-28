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
Certificate models for clients, servers and certificate authorities.
"""

from django.db import models
from libpurplenet.helpers import coalesce
from datetime import datetime

from libpurplenet import openssl

class Certificate(models.Model):
    common_name = models.CharField(max_length=128)
    granted = models.DateTimeField()
    expires = models.DateTimeField()
    revoked = models.DateTimeField(null=True, blank=True)
    revoked_by = models.ForeignKey("Client", null=True, blank=True,
        related_name="revoked_%(class)s_set")

    @property
    def timestamp(self):
        if self.revoked is not None:
            return self.revoked
        else:
            return self.granted

    @property
    def ca_name(self):
        return self.ca.common_name

    @property
    def is_revoked(self):
        return (self.revoked is not None)

    @property
    def org(self):
        return self.ca.owner
    
    def __unicode__(self):
        return self.common_name

    def revoke(self, revoked_by):
        """revoke()

        Revokes this certificate. Remember to call save() after revoke().
        """
        self.ca.revoke_certificate(self.common_name)
        self.revoked = datetime.now() # XXX this should come from cert data
        self.revoked_by = revoked_by
    
    class Admin:
        list_display = ('downloaded','common_name','user',
            'network','granted','revoked')
        list_filter = ['network','revoked','user']
        search_fields = ['user','network','common_name']

    class Meta:
        app_label = "openvpn_userinterface"
        abstract = True
        
    def _create_certificate(self):
        # TODO expiration
        key = openssl.generate_rsa_key()
        csr = openssl.create_csr(key=key, common_name=self.common_name, config=self.ca.config)
        crt = self.ca.sign_certificate(csr)
        
        return key, crt

class ClientCertificate(Certificate):
    ca = models.ForeignKey("ClientCA", related_name="certificate_set")
    network = models.ForeignKey("Network")
    owner = models.ForeignKey("Client", related_name="certificate_set")

    def create_certificate(self):
        return self._create_certificate()

    class Meta:
        app_label = "openvpn_userinterface"
    
class ServerCertificate(Certificate):
    ca = models.ForeignKey("ServerCA", blank=True, null=True,
        related_name="certificate_set")
    created_by = models.ForeignKey("Client", related_name="int_scrt_set")
    # REVERSE: user = OneToOne(Server)

    key = models.TextField(blank=True, null=True)
    certificate = models.TextField(blank=True, null=True)

    def create_certificate(self):
        if self.key is not None:
            raise AttributeError("Already created")
        
        key, crt = self._create_certificate()
        
        self.key = key
        self.crt = crt
        
        return key, crt

    class Meta:
        app_label = "openvpn_userinterface"

class CACertificate(Certificate):
    ca = models.ForeignKey("IntermediateCA", blank=True, null=True,
        related_name="certificate_set")

    # REVERSES: %s(class)_user = OneToOne(IntermediaryCA/ServerCA/ClientCA)

    # Here be dragons.
    @property
    def user(self):
        return coalesce(
            self.intermediateca_user,
            self.serverca_user,
            self.clientca_user
        )

    class Meta:
        app_label = "openvpn_userinterface"
    
    # No create_certificate here because mkca manages their own.

