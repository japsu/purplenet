#!/usr/bin/python

#
# OpenVPN Proof of Concept Implementation Project, 
# TLT-1600 Design Project in Telecommunications, 
# Department of Communications Engineering, 
# Tampere University of Technology (TUT)
#
# Copyright (c) 2008, 2009 Tuure Vartiainen
# 
#

import site
import os

SITE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
site.addsitedir(SITE_DIR)

os.environ["DJANGO_SETTINGS_MODULE"] = "openvpnweb.settings"
from django.conf import settings

from openvpnweb.certlib.openssl import generate_crl

EXIT_SUCCESS = 0
EXIT_FAILURE = 1

def main():
	# Just generate new CRL.
	generate_crl()

	return EXIT_SUCCESS

if __name__ == "__main__" and False:
	try:
		sys.exit(main())
	except Exception, e:
		print "ERROR: Exception: %s" % e
