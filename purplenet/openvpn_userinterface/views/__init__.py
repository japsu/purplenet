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
View functions for PurpleNet.
"""

from .loginout import login_page, logout_page
from .manage import (manage_page,
    manage_org_page, create_org_page,
    manage_network_page, create_network_page,
    manage_client_page, create_client_page,
    manage_server_page, create_server_page,
    manage_admin_group_page, create_admin_group_page,
    manage_org_map_page,
    add_client_to_admin_group_page, remove_client_from_admin_group_page,
    add_client_to_org_page, remove_client_from_org_page,
    add_admin_group_to_org_page, remove_admin_group_from_org_page,
    add_network_to_org_page, remove_network_from_org_page,
    add_network_to_server_page, remove_network_from_server_page,
    add_server_to_network_page, create_profile_page, manage_profile_page,
    inherit_profile_page, uninherit_profile_page, add_org_to_client_page,
    download_server_config_page, add_admin_group_to_client_page,
    add_org_to_network_page)
from .logs import manage_log_page
from .revoke import revoke_page
from .order import order_page
from .main import main_page
from .setup import setup_page
