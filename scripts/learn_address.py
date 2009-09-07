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
import sys

SITE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
site.addsitedir(SITE_DIR)

os.environ["DJANGO_SETTINGS_MODULE"] = "openvpnweb.settings"
from django.conf import settings

from openvpnweb.openvpn_userinterface.models import ClientCertificate


MODIFY_FW = os.path.abspath(os.path.join(os.path.dirname(__file__), "modify_ebtables.sh"))

EXIT_SUCCESS = 0
EXIT_FAILURE = 1

OVPN_OPERATIONS = {
	"add": "add",
	"update": "update",
	"delete": "delete",
}

def main():
	if len(sys.argv) < 3:
		print "ERROR: Too few arguments."

		return EXIT_FAILURE

	# Parameters
	operation = sys.argv[1]
	address = sys.argv[2]

	if operation == OVPN_OPERATIONS["delete"]:
		os.system("%s delete %s" % (MODIFY_FW, address))
		
		return EXIT_SUCCESS

	common_name = sys.argv[3]
	cert = ClientCertificate.objects.get(common_name=common_name)

	if cert.is_revoked:
		return EXIT_FAILURE
		
	attributes = cert.network.profile.attributes
	vlans = attributes.get("vlan")

	# TODO vlanX -> ethX map

	if vlans:
		vlan = vlans[0]
		os.system("%s add %s %s" % (MODIFY_FW, address, vlan))

		return EXIT_SUCCESS

	return EXIT_FAILURE

if __name__ == "__main__":
	try:
		sys.exit(main())
	except Exception, e:
		print "ERROR: Exception: %s" % e
