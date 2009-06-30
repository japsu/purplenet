# vim: shiftwidth=4 expandtab

from django.db import models
from datetime import datetime

import certlib.openssl as openssl
from openvpnweb.helper_functions import generate_random_string 

class CertificateAuthority(models.Model):
    common_name = models.CharField(max_length=200, unique=True)
    config = models.CharField(max_length=200)

    CA_TYPE_CHOICES = (
        ("root", "ROOT"),
        ("server", "SERVER"),
        ("client", "CLIENT"), # FIXME misleading names?
        ("org", "ORGANIZATION"),
    )
    ca_type = models.CharField(max_length=30, choices=CA_TYPE_CHOICES)

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

class Org(models.Model):
    name = models.CharField(max_length=30, unique=True)
    ca = models.ForeignKey(CertificateAuthority)
    cn_suffix = models.CharField(max_length=30)        

    def _get_ca_name(self):
        return self.ca.common_name
    def _set_ca_name(self, value):
        self.ca = CertificateAuthority.objects.get(common_name=value)
    ca_name = property(_get_ca_name, _set_ca_name)

    def __unicode__(self):
        return self.name

    def get_random_cn(self):
        return generate_random_string() + self.cn_suffix
    
    class Admin: pass

class Client(models.Model):
    name = models.CharField(max_length=30)
    orgs = models.ManyToManyField(Org, null=True)
    
    def __unicode__(self):
        return self.name

    class Admin: pass
                            
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
    
    def __unicode__(self):
        return self.name

    class Admin: pass

class NetworkProfile(models.Model):
    name = models.CharField(max_length=30)
    inherited_profiles = models.ManyToManyField('self', null=True, blank=True)

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
    
class Certificate(models.Model):
    common_name = models.CharField(max_length=30)
    ca = models.ForeignKey(CertificateAuthority)
    granted = models.DateTimeField()
    revoked = models.DateTimeField(null=True, blank=True)
    user = models.ForeignKey(Client)
    network = models.ForeignKey(Network)
    downloaded = models.BooleanField(default=False)

    def _get_timestamp(self):
        if self.revoked is not None:
            return self.revoked
        else:
            return self.granted
    timestamp = property(_get_timestamp)

    def _get_ca_name(self):
        return self.ca.common_name
    ca_name = property(_get_ca_name)

    def _is_revoked(self):
        return (self.revoked is not None)
    is_revoked = property(_is_revoked)
    
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

