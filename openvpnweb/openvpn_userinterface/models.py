# vim: shiftwidth=4 expandtab

from django.db import models
from django.contrib.auth.models import User, Group
from datetime import datetime

import certlib.openssl as openssl
from certlib.enums import CAType
from certlib.helpers import coalesce
from openvpnweb.helper_functions import generate_random_string 

class CertificateAuthority(models.Model):
    config = models.CharField(max_length=200)
    owner = models.ForeignKey("Org", null=True, blank=True,
        related_name="owned_%s(class)_set")

    certificate = models.OneToOneField("CACertificate", null=True,
        blank=True, related_name="%s(class)_user")

    @property
    def common_name(self):
        return self.certificate.common_name

    def __unicode__(self):
        return self.common_name

    def sign_certificate(self, csr):
        """sign_certificate(csr) -> signed certificate

        Signs the supplied Certificate Signing Request with this CA
        and returns the signed certificate. The CSR parameter and the
        return value are strings that contain the X.509 data in a
        format readable by OpenSSL, preferably PEM.
        """
        return openssl.sign_certificate(csr, config=self.config)

    def generate_crl(self):
        return openssl.generate_crl(config=self.config)

    def revoke_certificate(self, common_name):
        return openssl.revoke_certificate(common_name, config=self.config)    
    class Admin:
        pass
    
    class Meta:
        verbose_name_plural = "Certificate Authorities"    
        abstract = True

class ClientCA(CertificateAuthority):
    # REVERSE: user = OneToOne(Org)
    pass

class ServerCA(CertificateAuthority):
    # REVERSE: user = OneToOne(Server)
    pass

class IntermediateCA(CertificateAuthority):
    pass

class Org(models.Model):
    group = models.OneToOneField(Group)
    client_ca = models.ForeignKey(ClientCA, related_name="user_set")
    cn_suffix = models.CharField(max_length=30)        

    @property
    def name(self):
        return self.group.name

    @property
    def ca_name(self):
        return self.ca.common_name

    def __unicode__(self):
        return self.name

    def get_random_cn(self):
        return generate_random_string() + self.cn_suffix
    
    class Admin: pass

class Certificate(models.Model):
    common_name = models.CharField(max_length=30)
    granted = models.DateTimeField()
    revoked = models.DateTimeField(null=True, blank=True)

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

    def revoke(self):
        """revoke()

        Revokes this certificate. Remember to call save() after revoke().
        """
        self.ca.revoke_certificate(self.common_name)
        self.revoked = datetime.now()
    
    class Admin:
        list_display = ('downloaded','common_name','user',
            'network','granted','revoked')
        list_filter = ['network','revoked','user']
        search_fields = ['user','network','common_name']

    class Meta:
        abstract = True

class CACertificate(Certificate):
    ca = models.ForeignKey(IntermediateCA, blank=True, null=True,
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
    

class ServerCertificate(Certificate):
    ca = models.ForeignKey(ServerCA, blank=True, null=True,
        related_name="certificate_set")
    # REVERSE: user = OneToOne(Server)

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
    certificate = models.OneToOneField(ServerCertificate,
        related_name="user")
    
    def __unicode__(self):
        return self.name

    class Admin: pass

class NetworkProfile(models.Model):
    name = models.CharField(max_length=30)
    inherited_profiles = models.ManyToManyField('self', null=True,
        blank=True, symmetrical=False, related_name="inherited_by")
    # REVERSE: inherited_by = ManyToMany(self)

class NetworkAttributeType(models.Model):
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=2000)
    regex = models.CharField(max_length=200)

class NetworkAttribute(models.Model):
    profile = models.ForeignKey(NetworkProfile)
    attribute = models.ForeignKey(NetworkAttributeType)
    value = models.CharField(max_length=200)

class Network(models.Model):
    name = models.CharField(max_length=30)
    org = models.ForeignKey(Org)
    server = models.ForeignKey(Server)
    profiles = models.ManyToManyField(NetworkProfile, blank=True, null=True)
    
    def __unicode__(self):
        return self.name

    class Admin: pass

class ClientCertificate(Certificate):
    network = models.ForeignKey(Network)
    # REVERSE: user = OneToOne(Client)
    pass
    
class Client(models.Model):
    user = models.OneToOneField(User)
    orgs = models.ManyToManyField(Org, blank=True,
        related_name="clients")
    certificate = models.OneToOneField(ClientCertificate,
        related_name="user")
    
    @property
    def name(self):
        return self.user.username

    def __unicode__(self):
        return self.name

    def may_revoke(self, certificate):
        # TODO Admins may revoke other certs, too.
        return certificate.user == self or \
            self.may_manage(certificate.ca.org)

    def may_manage(self, org):
        # XXX Stub
        return org in self.orgs.all()

    def may_view_management_pages(self):
        # XXX Stub
        return True

    def get_managed_organizations(self):
        # XXX Stub
        return self.orgs

    class Admin: pass
