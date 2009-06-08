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

OPENSSL = "/usr/bin/openssl"

DEFAULT_CONFIG = "/etc/ssl/openssl.cnf"
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

def generate_rsa_key(key_length=2048, config=DEFAULT_CONFIG):
	# config taken just for symmetry
	# openssl genrsa does not accept -config

	log.debug("Generating a %d-bit RSA private key", key_length)	

	return _run("genrsa", "%d" % key_length)

def create_csr(key, config=DEFAULT_CONFIG):
	log.debug("Creating CSR")

	return _run("req", "-config", config, "-batch",
		"-new", "-key", "/dev/stdin",
		input=key
	)

def create_self_signed_certificate(key, config=DEFAULT_CONFIG):
	log.debug("Creating a self-signed certificate")

	return _run("req", "-config", config, "-batch",
		"-new", "-x509", "-key", "/dev/stdin",
		input=key
	)

def create_self_signed_keypair(key_length=2048, config=DEFAULT_CONFIG):
	key = generate_rsa_key(key_length, config)
	cert = create_self_signed_certificate(key, config)

	return key, cert

def sign_certificate(csr, config=DEFAULT_CONFIG):
	log.debug("Signing a CSR")

	return _run("ca", "-config", config, "-batch", input=csr)
