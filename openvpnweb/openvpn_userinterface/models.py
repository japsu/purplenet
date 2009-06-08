from subprocess import Popen

import certlib.openssl

# TODO File locking?

class CA(models.Model):
	name = models.CharField(max_length=200)
	dir = models.CharField(max_length=200)

	def sign_certificate(self, csr):
		"""sign_certificate(csr) -> signed certificate
		
		Signs the supplied Certificate Signing Request with this CA
		and returns the signed certificate. The CSR parameter and the
		return value are strings that contain the X.509 data in a
		format readable by OpenSSL, preferably PEM.
		"""
		return openssl.sign_certificate(self.dir, csr)

	def revoke_certificate(self, cert):
		return openssl.revoke_certificate(self.dir, cert)

	def generate_crl(self):
		return openssl.generate_crl(self.dir)
