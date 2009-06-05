from subprocess import Popen

# TODO File locking?

# XXX
OPENSSL = "/usr/bin/openssl"

class OpenSSLError(RuntimeError):
	pass

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
		openssl = Popen([OPENSSL, "ca", "-batch", "-config", self.config])
		err, cert = openssl.communicate(csr)
		if openssl.returncode != 0:
			raise OpenSSLError(err)

	def revoke_certificate(self, cert):
		pass

	def generate_crl(self):
		pass
