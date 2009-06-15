# vim: shiftwidth=4 expandtab

from django.db import models

import certlib.openssl as openssl

class CertificateAuthority(models.Model):
    common_name = models.CharField(max_length=200, unique=True)
    config = models.CharField(max_length=200)
    parent = models.ForeignKey('self', null=True, blank=True)

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

    class Admin:
        pass
    
    class Meta:
        verbose_name_plural = "Certificate Authorities"    

class Org(models.Model):
    name = models.CharField(max_length=30)
    ca = models.ForeignKey(CertificateAuthority)
    cn_suffix = models.CharField(max_length=30)        

    def _get_ca_name(self):
        return self.ca.common_name
    def _set_ca_name(self, value):
        self.ca = CertificateAuthority.objects.get(common_name=value)
    ca_name = property(_get_ca_name, _set_ca_name)

    def __str__(self):
        return self.name
    def __repr__(self):
        return self.name
    
    class Admin: pass

class Client(models.Model):
    name = models.CharField(max_length=30)
    orgs = models.ManyToManyField(Org, null=True)
    def __str__(self):
        return self.name
    
    def __repr__(self):
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
    
    def __str__(self):
        return self.name
        
    def __repr__(self):
        return self.name
                
    class Admin: pass

class Network(models.Model):
    name = models.CharField(max_length=30)
    org = models.ForeignKey(Org)
    server = models.ForeignKey(Server)
    
    def __str__(self):
        return self.name
   
    def __repr__(self):
        return self.name
    
    class Admin: pass
    
# TODO rename class to NetworkAttribute (PEP-8)
class Network_attribute(models.Model):
    name = models.CharField(max_length=30)
    value = models.CharField(max_length=30)
    networks = models.ManyToManyField(Network)
    
    def __str__(self):
        return self.name
    
    class Admin:
        pass

    class Meta:
        # TODO unnecessary after class rename
        verbose_name_plural = "Network attributes"        

class Certificate(models.Model):
    common_name = models.CharField(max_length=30)
    ca = models.ForeignKey(CertificateAuthority)
    timestamp = models.DateTimeField()
    revoked = models.BooleanField(default=False)
    user = models.ForeignKey(Client)
    network = models.ForeignKey(Network)
    downloaded = models.BooleanField(default=False)

    def _get_ca_name(self):
        return self.ca.common_name
    def _set_ca_name(self, value):
        self.ca = CertificateAuthority.objects.get(common_name=value)
    ca_name = property(_get_ca_name, _set_ca_name)
    
    def __str__(self):
        return self.common_name
    def __repr__(self):
        return self.common_name

    def revoke(self):
        """revoke()

        Revokes this certificate. Remember to call save() after revoke().
        """
        self.ca.revoke_certificate(self.common_name)
        self.revoked = True
    
    class Admin:
        list_display = ('revoked','downloaded','common_name','user','network','timestamp')
        list_filter = ['network','revoked','user']
        search_fields = ['user','network','common_name']

