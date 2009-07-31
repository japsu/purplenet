# encoding: utf-8
# vim: shiftwidth=4 expandtab

from django.db import models
from certlib.helpers import coalesce
from datetime import datetime

class Certificate(models.Model):
    common_name = models.CharField(max_length=30)
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

class ClientCertificate(Certificate):
    ca = models.ForeignKey("ClientCA", related_name="certificate_set")
    network = models.ForeignKey("Network")
    owner = models.ForeignKey("Client", related_name="certificate_set")

    class Meta:
        app_label = "openvpn_userinterface"
    
class ServerCertificate(Certificate):
    ca = models.ForeignKey("ServerCA", blank=True, null=True,
        related_name="certificate_set")
    # REVERSE: user = OneToOne(Server)

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

