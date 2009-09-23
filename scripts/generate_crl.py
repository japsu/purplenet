#!/bin/sh
# encoding: utf-8
# vim: shiftwidth=4 expandtab
#
# PurpleNet - a Web User Interface for OpenVPN
# Copyright (C) 2009  Tuure Vartiainen
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
import os, sys

SITE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
site.addsitedir(SITE_DIR)

os.environ["DJANGO_SETTINGS_MODULE"] = "purplenet.settings"
from django.conf import settings

from libpurplenet.openssl import generate_crl
from purplenet.openvpn_userinterface.models import ClientCA

EXIT_SUCCESS = 0
EXIT_FAILURE = 1

def main():
	# XXX hard-coded CA - iterate over all CAs
	config = ClientCA.objects.get(certificate__common_name__exact="TLT").config
	
	# Just generate new CRL.
	generate_crl(config=config)

	return EXIT_SUCCESS

if __name__ == "__main__":
	try:
		sys.exit(main())
	except Exception, e:
		print "ERROR: Exception: %s" % e
