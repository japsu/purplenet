# encoding: utf-8
# vim: shiftwidth=4 expandtab
#
# PurpleNet - a Web User Interface for OpenVPN
# Copyright (C) 2009  Santtu Pajukanta
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

"""
Configuration data for the certificate authority generation script.
"""

from __future__ import absolute_import

import os

from .enums import CAType

OPENSSL = "/usr/bin/openssl"
DEFAULT_CONFIG = "/etc/ssl/openssl.cnf"
DEFAULT_CA_NAME = "CA_default"

# TODO mkca.cnf should probably reside somewhere under /usr/share.
MKCA_CONFIG = os.path.join(os.path.dirname(__file__), "mkca.cnf")

base = dict(
	default_days = 365,
	default_crl_days = 30,
	basic_constraints = "critical,CA:false",
	key_usage = "critical,digitalSignature,keyEncipherment"
)

ca = dict(base,
	default_days = 3650,
	basic_constraints = "CA:true",
	key_usage = "critical,cRLSign,keyCertSign"
)

server = dict(base,
	extended_key_usage = "critical,serverAuth"
)

client = dict(base,
	extended_key_usage = "critical,clientAuth"
)

config_data = {
	CAType.CA : ca,
	CAType.SERVER : server,
	CAType.CLIENT : client
}

