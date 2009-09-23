#!/usr/bin/env python
# encoding: utf-8
# vim: shiftwidth=4 expandtab
#
# PurpleNet - a Web User Interface for OpenVPN
# Copyright (C) 2008, 2009  Santtu Pajukanta, Tuure Vartiainen
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

import site
import os
import sys

SITE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
site.addsitedir(SITE_DIR)

os.environ["DJANGO_SETTINGS_MODULE"] = "purplenet.settings"
from django.conf import settings

from purplenet.openvpn_userinterface.models import ClientCertificate


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
	vlan = attributes.get("vlan")

	# TODO vlanX -> ethX map

	if vlan:
		os.system("%s add %s %s" % (MODIFY_FW, address, vlan))

		return EXIT_SUCCESS

	return EXIT_FAILURE

if __name__ == "__main__":
	try:
		sys.exit(main())
	except Exception, e:
		print "ERROR: Exception: %s" % e
