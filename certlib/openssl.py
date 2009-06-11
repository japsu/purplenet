# -*- coding: utf-8 -*-
#
# OpenSSL Certificate Authority generation script
# Department of Communications Engineering, 
# Tampere University of Technology (TUT)
#
# Copyright (c) 2009 Santtu Pajukanta
# 
# 

from __future__ import absolute_import

import sys, os
import logging
import subprocess

from collections import defaultdict
from openvpnweb.certificate_manager import _parse_conf_value

from .data import DEFAULT_CONFIG, OPENSSL

log = logging.getLogger("certlib")

class OpenSSLError(RuntimeError):
	pass

def _run(*args, **kwargs):
	"""_run(*args, input=None) -> String
	
	Executes OpenSSL using the supplied arguments and return its output.
	If a keyword argument named input is provided, writes its contents
	(a string) into the standard input of the OpenSSL process. If OpenSSL
	exits with a non-zero exit status, an OpenSSLError is raised with the
	messages written by OpenSSL into its standard error stream as the
	payload of the exception.
	"""
	input = kwargs.get("input", None)

	cmdline = [OPENSSL]
	cmdline.extend(args)

	log.debug("Executing %s", cmdline)

	openssl = subprocess.Popen(cmdline,
		stdout=subprocess.PIPE, stderr=subprocess.PIPE,
		stdin=subprocess.PIPE if input is not None else None
	)

	stdoutdata, stderrdata = openssl.communicate(input)

	if openssl.returncode is None:
		log.error("OpenSSL did not terminate after signalling EOF!")
		raise RuntimeError()
	elif openssl.returncode > 0:
		log.error("OpenSSL failed with exit status %d",
			openssl.returncode)
		raise OpenSSLError(stderrdata)
	elif openssl.returncode < 0:
		log.error("OpenSSL was killed by signal %d",
			-openssl.returncode)
		raise OpenSSLError(stderrdata)

	return stdoutdata

DN_COMPONENTS = [
	# (shorthand, [kwarg, ...], config key)
	("C", ["countryName", "country_name"], "countryName_default"),
	("L", ["localityName", "locality_name"], "localityName_default"),
	("O", ["organizationName", "organization_name"], "organizationName_default"),
	("OU", ["organizationalUnitName", "organizational_unit_name"], "organizationalUnitName_default"),
	("CN", ["commonName", "common_name"], "commonName_default"),
]

def _process_dn_components(components):
	kwa_to_short = {}
	ckey_to_short = {}
	ckeys = []
	shorts = []
	for shorthand, kws, ckey in components:
		ckeys.append(ckey)
		shorts.append(shorthand)
		ckey_to_short[ckey] = shorthand
		for kw in kws:
			kwa_to_short[kw] = shorthand
	return kwa_to_short, ckey_to_short, ckeys, shorts

DN_KWA_SHORT, DN_CKEY_SHORT, DN_CKEYS, DN_SHORTS = _process_dn_components(DN_COMPONENTS)

def _dn_escape(s):
	# TODO verify
	return s.replace("/",r"\/")

def _make_dn(**kwargs):
	if kwargs.has_key("config"):
		config = kwargs["config"]
		del kwargs["config"]
	else:
		config = DEFAULT_CONFIG

	defaults = _parse_conf_value("req_distinguished_name", *DN_CKEYS, config=config)
	defaults = ((DN_CKEY_SHORT[key], value) for key, value in defaults.iteritems())
	kwargs = dict((DN_KWA_SHORT[key], value) for key, value in kwargs.iteritems() if DN_KWA_SHORT.has_key(key))
	values = dict(defaults, **kwargs)

	return "".join("/%s=%s" % (key, _dn_escape(values[key])) for key in DN_SHORTS if values.has_key(key))
	

def generate_rsa_key(key_length=2048, config=DEFAULT_CONFIG):
	"""generate_rsa_key(key_length=2048, config=DEFAULT_CONFIG) -> String

	Generates a private RSA key of the specified length. The config
	argument is provided only for symmetry and is ignored. The generated
	RSA key is returned as a string in the PEM format.
	"""
	log.debug("Generating a %d-bit RSA private key", key_length)	

	return _run("genrsa", "%d" % key_length)

def create_csr(key, common_name, config=DEFAULT_CONFIG):
	"""create_csr(common_name, key, config=DEFAULT_CONFIG) -> String

	Creates a Certificate Signing Request using the supplied common name
	(CN) and private key. Other attributes are taken from the supplied
	configuration file or, the config parameter being absent, the default
	configuration file. The generated CSR is returned as a string in the
	PEM format.
	"""
	log.debug("Creating CSR")

	subject = _make_dn(common_name=common_name, config=config)

	return _run("req", "-config", config, "-batch",
		"-new", "-key", "/dev/stdin",
		"-subj", subject,
		input=key
	)

def create_self_signed_certificate(key, common_name, extensions="crt_ext", config=DEFAULT_CONFIG):
	"""create_self_signed_certificate(common_name, key,
		extensions="crt_ext", config=DEFAULT_CONFIG) -> str

	Creates a self-signed X.509 test certificate using the supplied
	common name (CN) and private key. Other attributes are taken from the
	supplied configuration file or, in its absence, the default
	configuration file. The generated certificate is returned as a string
	in the PEM format.
	"""
	log.debug("Creating a self-signed certificate")

	subject = _make_dn(common_name=common_name, config=config)

	params = [
		"req", "-config", config, "-batch",
		"-new", "-x509", "-key", "/dev/stdin",
		"-subj", subject
	]

	if extensions is not None:
		params.extend(("-extensions", extensions))

	return _run(*params, input=key)

def create_self_signed_keypair(common_name, key_length=2048, config=DEFAULT_CONFIG):
	key = generate_rsa_key(key_length, config=config)
	cert = create_self_signed_certificate(key, common_name=common_name, config=config)

	return key, cert

def sign_certificate(csr, extensions="crt_ext", config=DEFAULT_CONFIG):
	log.debug("Signing a CSR")

	params = ["ca", "-config", config, "-batch", "-noemailDN", "-in", "/dev/stdin"]

	if extensions is not None:
		params.extend(("-extensions", extensions))

	return _run(*params, input=csr)


