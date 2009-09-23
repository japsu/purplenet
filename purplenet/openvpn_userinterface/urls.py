# encoding: utf-8
# vim: shiftwidth=4 expandtab
#
# PurpleNet - a Web User Interface for OpenVPN
# Copyright (C) 2009  Santtu Pajukanta
# Copyright (C) 2008, 2009  Tuure Vartiainen, Antti Niemelä, Vesa Salo
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
Main request dispatcher for PurpleNet.
"""

from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from purplenet.openvpn_userinterface.views import *

urlpatterns = patterns('',
    url(r'^$', main_page, name="main_page"),
    
    url(r'^login/$', login_page, name="login_page"),
    url(r'^logout/$', logout_page, name="logout_page"),
    
    url(r'^revoke/(?P<cert_id>\d+)$', revoke_page, name="revoke_page"),
    url(r'^order/(?P<org_id>\d+)/(?P<network_id>\d+)$', order_page,
        name="order_page"),

    url(r'^manage/$', manage_page, name="manage_page"),
    url(r'^manage/log/$', manage_log_page, name="manage_log_page"),
    
    url(r'^manage/server/(?P<server_id>\d+)/$', manage_server_page,
        name="manage_server_page"),
    url(r'^manage/server/create/$', create_server_page,
        name="create_server_page"),
    url(r'^manage/server/(?P<server_id>\d+)/addnetwork/$',
        add_network_to_server_page, name="add_network_to_server_page"),
    url(r'^manage/server/(?P<server_id>\d+)/removenetwork/(?P<network_id>\d+)/$',
        remove_network_from_server_page, name="remove_network_from_server_page"),
    url(r'^manage/server/(?P<server_id>\d+)/config/$',
        download_server_config_page, name="download_server_config_page"),
    
    url(r'^manage/network/(?P<network_id>\d+)/$',
        manage_network_page, name="manage_network_page"),
    url(r'^manage/network/create/$', create_network_page,
        name="create_network_page"),
    url(r'^manage/network/(?P<network_id>\d+)/addserver/$',
        add_server_to_network_page, name="add_server_to_network_page"),
    url(r'^manage/network/(?P<network_id>\d+)/removeserver/(?P<server_id>\d+)/$',
        remove_network_from_server_page, name="remove_server_from_network_page"),
    url(r'^manage/network/(?P<network_id>\d+)/addorg/$',
        add_org_to_network_page, name="add_org_to_network_page"),
    url(r'^manage/network/(?P<network_id>\d+)/removeorg/(?P<org_id>\d+)/$',
        remove_network_from_org_page, name="remove_org_from_network_page"),
    
    url(r'manage/profile/(?P<profile_id>\d+)/$',
        manage_profile_page, name="manage_profile_page"),
    url(r'manage/profile/create$',
        manage_profile_page, name="create_profile_page"),
    url(r'manage/profile/(?P<inheritor_id>\d+)/inherit/$',
        inherit_profile_page, name="inherit_profile_page"),
    url(r'manage/profile/(?P<inheritor_id>\d+)/uninherit/(?P<target_id>\d+)/$',
        uninherit_profile_page, name="uninherit_profile_page"),
    
    url(r'^manage/org/(?P<org_id>\d+)/$', manage_org_page,
        name="manage_org_page"),
    url(r'^manage/org/(?P<org_id>\d+)/addclient/$', add_client_to_org_page,
        name="add_client_to_org_page"),
    url(r'^manage/org/(?P<org_id>\d+)/removeclient/(?P<client_id>\d+)/$',
        remove_client_from_org_page, name="remove_client_from_org_page"),
    url(r'^manage/org/(?P<org_id>\d+)/addadmins/$', add_admin_group_to_org_page,
        name="add_admin_group_to_org_page"),
    url(r'^manage/org/(?P<org_id>\d+)/removeadmins/(?P<admin_group_id>\d+)/$',
        remove_admin_group_from_org_page,
        name="remove_admin_group_from_org_page"),
    url(r'^manage/org/(?P<org_id>\d+)/addnetwork/$',
        add_network_to_org_page, name="add_network_to_org_page"),
    url(r'^manage/org/(?P<org_id>\d+)/removenetwork/(?P<network_id>\d+)/$',
        remove_network_from_org_page, name="remove_network_from_org_page"),
    url(r'^manage/org/create/$', create_org_page,
        name="create_org_page"),
        
    url(r'^manage/client/(?P<client_id>\d+)/$', manage_client_page,
        name="manage_client_page"),
    url(r'^manage/client/create/$', create_client_page,
        name="create_client_page"),
    url(r'^manage/client/(?P<client_id>\d+)/addorg/$', add_org_to_client_page,
        name="add_org_to_client_page"),
    url(r'^manage/client/(?P<client_id>\d+)/removeorg/(?P<org_id>\d+)/$',
        remove_client_from_org_page, name="remove_client_from_org_page"),
    url(r'^manage/client/(?P<client_id>\d+)/addgroup/$', add_admin_group_to_client_page,
        name="add_admin_group_to_client_page"),
    url(r'^manage/client/(?P<client_id>\d+)/removegroup/(?P<admin_group_id>\d+)',
        remove_client_from_admin_group_page, name="remove_admin_group_from_client_page"),
    
    url(r'^manage/group/(?P<admin_group_id>\d+)$', manage_admin_group_page,
        name="manage_admin_group_page"),
    url(r'^manage/group/(?P<admin_group_id>\d+)/removeclient/(?P<client_id>\d+)$',
        remove_client_from_admin_group_page, name="remove_client_from_admin_group_page"),
    url(r'^manage/group/(?P<admin_group_id>\d+)/addclient/$',
        add_client_to_admin_group_page, name="add_client_to_admin_group_page"),
    url(r'^manage/group/create/$', create_admin_group_page,
        name="create_admin_group_page"),
        
    url(r'^manage/orgmap/$', manage_org_map_page,
        name="manage_org_map_page"),
        
    url(r'^setup/$', setup_page, name="setup_page"),
    url(r'^setup_complete/$', direct_to_template,
        {'template':'openvpn_userinterface/setup_complete.html'},
        name="setup_complete_page"),
)
