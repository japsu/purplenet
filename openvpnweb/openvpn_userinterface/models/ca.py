# encoding: utf-8
# vim: shiftwidth=4 expandtab

from django.db import models
import os

import certlib.openssl as openssl
import certlib.mkca as mkca
from certlib.enums import CAType, SignMode

class CertificateAuthority(models.Model):
    dir = models.CharField(max_length=200)
    owner = models.ForeignKey("Org", null=True, blank=True,
        related_name="%(class)s_set")

    certificate = models.OneToOneField("CACertificate", null=True,
        blank=True, related_name="%(class)s_user")

    @property
    def config(self):
        return os.path.join(self.dir, mkca.OPENSSL_CONFIG_FILE_NAME)

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
    def get_ca_certificate_path(self):
        return openssl.get_ca_certificate_path(config=self.config)

    def _create_ca(self, ca_type):
        ca = self.certificate.ca        

        mkca.mkca(
            dir=self.dir,
            common_name=self.certificate.common_name,
            ca_type=ca_type,
            sign_mode=SignMode.USE_CA if ca else SignMode.SELF_SIGN,
            copy_dir=settings.OPENVPNWEB_OPENSSL_CHAIN_DIR,
            config=ca.config if ca else None, # XXX
            force=False
        )

    class Admin:
        pass
    
    class Meta:
        app_label = "openvpn_userinterface"
        verbose_name_plural = "Certificate Authorities"    
        abstract = True

class ClientCA(CertificateAuthority):
    # REVERSE: certificates = ForeignKey(ClientCertificate)
    # REVERSE: users = ForeignKey(Org)

    def create_ca(self):
        return super(ClientCA, self)._create_ca(CAType.CLIENT)

    class Meta:
        app_label = "openvpn_userinterface"
    
class ServerCA(CertificateAuthority):
    # REVERSE: user_set = ForeignKey(Network)

    def create_ca(self):
        return super(ServerCA, self)._create_ca(CAType.SERVER)

    class Meta:
        app_label = "openvpn_userinterface"

class IntermediateCA(CertificateAuthority):
    def create_ca(self):
        return super(IntermediateCA, self)._create_ca(CAType.CA)

    class Meta:
        app_label = "openvpn_userinterface"

