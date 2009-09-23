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
Models of the PurpleNet OpenVPN user interface application.
"""

# Remember to add
#
#     class Meta:
#         app_label = "openvpn_userinterface"
#
# in all new models to make Django find them.

from .ca import CertificateAuthority, IntermediateCA, ClientCA, ServerCA
from .certificates import (Certificate, ClientCertificate, ServerCertificate,
    CACertificate)
from .client import Client
from .logging import LogEntry
from .network import (NetworkProfile, NetworkAttribute, NetworkAttributeType,
    Network, ProfileInheritance, CircularInheritance, MixedModes,
    MixedProtocols, NoServers)
from .org import Org, AdminGroup
from .org_map import (OrgMapping, MappingType, MappingElement, load_org_map,
    dump_org_map, validate_org_map)
from .server import Server
from .siteconfig import SiteConfig, InterestingEnvVar

