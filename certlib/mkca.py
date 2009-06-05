#!/usr/bin/env python
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

from .helpers import FileExists, mkdir_check, enum_check, write_file
from .enums import Exit, CAType, SignMode
from . import helpers, openssl_data

import sys, os
import logging
import random

OPENSSL_CONFIG_TEMPLATE_NAME = "certlib/openssl.cnf"

# Make sure these correspond to your configuration template.
# TODO Should these be variables in the template?
NEW_CERTS_DIR_NAME = "new_certs"
DATABASE_FILE_NAME = "index.txt"
CERT_SERIAL_FILE_NAME = "cert-serial"
CRL_SERIAL_FILE_NAME = "crl-serial"
OPENSSL_CONFIG_FILE_NAME = "openssl.cnf"

log = None

def mkca(dir, ca_type=CAType.CLIENT, sign_mode=SignMode.SELF_SIGN,
		sign_ca=None, force=False):
	global log
	log = logging.getLogger("certlib")

	dir = os.path.abspath(dir)
	new_certs_dir = os.path.join(dir, NEW_CERTS_DIR_NAME)
	database_file = os.path.join(dir, DATABASE_FILE_NAME)
	cert_serial_file = os.path.join(dir, CERT_SERIAL_FILE_NAME)
	crl_serial_file = os.path.join(dir, CRL_SERIAL_FILE_NAME)
	openssl_config_file = os.path.join(dir, OPENSSL_CONFIG_FILE_NAME)

	log.debug("sign_mode = %s", sign_mode)
	log.debug("sign_ca = %s", sign_ca)
	log.debug("force = %s", force)
	log.debug("dir = %s", dir)
	log.debug("new certs dir = %s", new_certs_dir)
	log.debug("database file = %s", database_file)
	log.debug("cert serial file = %s", cert_serial_file)
	log.debug("crl serial file = %s", crl_serial_file)
	log.debug("openssl config file = %s", openssl_config_file)

	# Make directories
	mkdir_check(dir, force)
	mkdir_check(new_certs_dir, force)

	# Create an empty database file
	write_file(database_file, '', force)
	
	# Generate random serials for certs and CRLs and write them down
	cert_serial = random.randint(0, 2**31-1)
	crl_serial = random.randint(0, 2**31-1)
	write_file(cert_serial_file, '%x' % cert_serial, force)
	write_file(crl_serial_file, '%x' % crl_serial, force)

	# Initialize the context with type-specific values from
	# openssl_data.py and fill in the rest of the gaps.
	ctx = dict(openssl_data.config_data[ca_type], dir=dir)

	# Render the OpenSSL configuration file from a template
	helpers.render_to_file(openssl_config_file,
		OPENSSL_CONFIG_TEMPLATE_NAME, ctx, force)

if __name__ == "__main__":
	main(sys.argv[1:])
