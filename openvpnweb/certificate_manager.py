#
# Project work: TLT-1600 2007 OpenVPN proof of concept implementation.
#
# Author: Tuure Vartiainen (tuure.vartiaine@tut.fi)
#

# TODO port to use subprocess module
# TODO use separate config

"Certificate manager is a module for creating and revokating x.509 certificates."

__all__ = ["get_certificate_authoroties", "create_certificate", "create_pkcs12", "create_crl", "revoke_certificate"]

import os
import re
from shutil import copyfile

_SSL_DIR = "/etc/ssl/"
_SSL_CONF = _SSL_DIR + "openssl.cnf"
_SSL_KEYS = _SSL_DIR + "privates/"
_SSL_REQS = _SSL_DIR + "requests/"
_SSL_CERTS = _SSL_DIR + "certs/"
_SSL_PKCS12 = _SSL_DIR + "client_pkcs12/"

_SSL_SERVER_CA = _SSL_CERTS + "openvpn-ca-server.crt"

_SSL_DEFAULT_KEY_SIZE = 2048

def _parse_database(ca_name, common_name=""):
	"""
	Parser the openssl certificate database (txt).
	
	Returns a dictionary of certificates signed by a given CA.
	"""
	
	regexp_ca = re.compile("^\s*\[\s*(%s)\s*\]" % ca_name)
      	conf_file = open(_SSL_CONF, "r")
	
	# Start iterating the file
	for line in conf_file:
		if regexp_ca.match(line):
			break
	else:
		raise Exception("No given CA was found.")
	
	regexp_database = re.compile("^\s*database\s*=\s*(\S+)", re.IGNORECASE)
	database_name = ""
	
	# Continue iterating the file
	for line in conf_file:
		if regexp_database.match(line):
			match = regexp_database.search(line)
			database_name = match.group(1)
			break
	else:
		raise Exception("No database file defined for given CA.")
	
	conf_file.close()

	regexp = ".*CN=(\S+)\s*$"

	if common_name != "":
		regexp = ".*CN=(%s)\s*$" % common_name
	
	regexp_cn = re.compile(regexp, re.IGNORECASE)
	database_file = open(database_name.replace("$dir/", _SSL_DIR), "r")
	
	certificates = {}
	
	seria = ""
	common_name = ""
	
	for line in database_file:
		if regexp_cn.match(line):
			match = regexp_cn.search(line)
			serial = line.split()[2]
			common_name = match.group(1)			
			
			certificates[common_name] = serial
	
	database_file.close()
	
	return certificates

def _parse_conf_value(section_name, *variable_names, **kwargs):
	"""
	Parser the openssl configuration file.
	
	Returns the dictionary of given variables.
	"""
	
	regexp_section = re.compile("^\s*\[\s*(%s)\s*\]" % section_name)
	conf_file = open(kwargs.get("config", _SSL_CONF), "r")

	# Start iterating the file
	for line in conf_file:
		if regexp_section.match(line):
			break
	else:
		raise Exception("No given section was found.")
	
	regexp_variable = re.compile("^\s*(\S+)\s*=\s*(\S+.*)", re.IGNORECASE)
	values = {}

	# Continue iterating the file
	for line in conf_file:
		if regexp_variable.match(line):
			match = regexp_variable.search(line)
			variable = match.group(1)
			value = match.group(2)

			if variable in variable_names:
				if not values.has_key(variable):
					values[variable] = value

	conf_file.close()
	
	return values

def get_certificate_authoroties():
	"""
	Lists certificate authoroties.
	
	Returns a list of certificate authoroties' names.
	"""
	
	regexp_ca = re.compile("^\s*\[\s*([^\]\s]+)\s*\]")
	regexp_cert = re.compile("^\s*certificate\s*=", re.IGNORECASE)
	conf_file = open(_SSL_CONF, "r")
	
	ca_list = []
	ca_name = None
	
	for line in conf_file:
		if regexp_ca.match(line):
			match = regexp_ca.search(line)
			ca_name = match.group(1)
		elif regexp_cert.match(line) and ca_name:
			ca_list.append(ca_name)
			ca_name = None

	conf_file.close()
	
	return ca_list

def _create_key(common_name, key_size=_SSL_DEFAULT_KEY_SIZE, params=""):
	"""
	Creates a new key pair.
	
	Returns the path to the created public key.
	"""
	
	key_filename = _SSL_KEYS + common_name + ".key"
	
	if os.system("openssl genrsa %s -out %s %d" % (params, key_filename, key_size)):
		os.remove(key_filename)
		
		raise Exception("Public key generation failed.")
	else:
		os.chmod(key_filename, 0600)
	
	return key_filename

def _create_request(common_name, key_filename):
	"""
	Creates a new certificate request.
	
	Returns the path to the created certificate request.
	"""
	
	req_filename = _SSL_REQS + common_name + ".req"
	
	if os.path.exists(req_filename):
		raise Exception("Certificate request already exists.")
	
	dn_components = ["countryName_default", "localityName_default", "organizationName_default",
			 "organizationalUnitName_default"]
	dn_prefixes = ('C', 'L', 'O', 'OU', 'CN')

	dn_values = _parse_conf_value("req_distinguished_name", *dn_components)
	dn_values["commonName"] = common_name

	dn_components.append("commonName")
	dn_fields = dict(zip(dn_components, dn_prefixes))

	subject = "".join(("/%s=%s" % (dn_fields[k], dn_values[k]) for k in dn_components))
	subject = subject.replace(" ", "\ ")
	
	if os.system("openssl req -new -key %s -out %s -subj %s" % (key_filename, req_filename, subject)):
		os.remove(req_filename)
		
		raise Exception("Certificate request generation failed.")
	else:
		os.chmod(req_filename, 0600)
	
	return req_filename

def create_certificate(ca_name, common_name):
	"""
	Creates a new certificate.
	
	Returns the path to the created certificate.
	"""
	
	key_filename = _create_key(common_name)
	req_filename = _create_request(common_name, key_filename)
	cert_filename = _SSL_CERTS + common_name + ".crt"
	
	if os.path.exists(cert_filename):
		raise Exception("Certificate already exists.")
	
	if os.system("openssl ca -batch -noemailDN -name %s -in %s" % (ca_name, req_filename)):
		raise Exception("Certificate signing failed.")
	
	certificates = _parse_database(ca_name, common_name)
	serial = certificates[common_name]
	
	conf = _parse_conf_value(ca_name, "new_certs_dir")
	new_certs_dir = conf["new_certs_dir"].replace("$dir/", _SSL_DIR)

	copyfile(new_certs_dir + "/" + serial + ".pem", cert_filename)

	return cert_filename

def create_pkcs12(common_name, params="-nodes"):
	"""
	Creates a new pkcs12 package.
	
	Returns the path to the created package.
	"""
	
	cert_filename = _SSL_CERTS + common_name + ".crt"
	key_filename = _SSL_KEYS + common_name + ".key"
	pkcs12_filename = _SSL_PKCS12 + common_name + ".p12"
	
	if not os.path.exists(cert_filename):
		raise Exception("No given certificate was found.")
	
	if os.system("openssl pkcs12 -export -passout pass: -chain %s -certfile %s -inkey %s -in %s -out %s" % (params, _SSL_SERVER_CA, key_filename, cert_filename, pkcs12_filename)):
		os.remove(pkcs12_filename)
		
		raise Exception("PKCS12 package generation failed.")
	else:
		os.chmod(pkcs12_filename, 0600)
	
	return pkcs12_filename

def create_crl(ca_name):
	"""
	Generates a new certificate revokation list.
	
	Returns nothing.
	"""

	conf = _parse_conf_value(ca_name, "crl_dir", "crl")
	crl_filename = conf["crl"].replace("$crl_dir", conf["crl_dir"].replace("$dir/", _SSL_DIR))

	if os.system("openssl ca -name %s -gencrl -out %s" % (ca_name, crl_filename)):
		raise Exception("Certificate revokation list generation failed.")

def revoke_certificate(ca_name, common_name):
	"""
	Revokes a certificate.
	
	Returns nothing.
	"""
	
	certificates = _parse_database(ca_name, common_name)
	serial = certificates[common_name]
	conf = _parse_conf_value(ca_name, "new_certs_dir")
	new_certs_dir = conf["new_certs_dir"].replace("$dir/", _SSL_DIR)
	cert_filename = new_certs_dir + "/" + serial + ".pem"
	
	if os.system("openssl ca -name %s -revoke %s" % (ca_name, cert_filename)):
		raise Exception("Certification revokation failed.")

	create_crl(ca_name)
