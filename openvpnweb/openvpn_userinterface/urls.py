# encoding: utf-8
# vim: shiftwidth=4 expandtab

from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from openvpnweb.openvpn_userinterface.views import *

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
        
    url(r'^manage/network/(?P<org_id>\d+)/(?P<network_id>\d+)/$',
        manage_network_page, name="manage_network_page"),
    url(r'^manage/network/create/$', create_network_page,
        name="create_network_page"),
        
    url(r'^manage/org/(?P<org_id>\d+)/$', manage_org_page,
        name="manage_org_page"),
    url(r'^manage/org/(?P<org_id>\d+)/addclient/$', add_client_to_org_page,
        name="add_client_to_org_page"),
    url(r'^manage/org/(?P<org_id>\d+)/removeclient/(?P<client_id>\d+)/$',
        remove_client_from_org_page, name="remove_client_from_org_page"),
    url(r'^manage/org/(?P<org_id>\d+)/addadmins/$', add_admin_group_to_org_page,
        name="add_admin_group_to_org_page"),
    url(r'^manage/org/(?P<org_id>\d+)/removeadmins/(?P<group_id>\d+)/$',
        remove_admin_group_from_org_page,
        name="remove_admin_group_from_org_page"),
    url(r'^manage/org/create/$', create_org_page,
        name="create_org_page"),
        
    url(r'^manage/client/(?P<client_id>\d+)/$', manage_client_page,
        name="manage_client_page"),
    url(r'^manage/client/create/$', create_client_page,
        name="create_client_page"),
        
    url(r'^manage/group/(?P<group_id>\d+)$', manage_group_page,
        name="manage_group_page"),
    url(r'^manage/group/(?P<group_id>\d+)/removeclient/(?P<client_id>\d+)$',
        remove_client_from_group_page, name="remove_client_from_group_page"),
    url(r'^manage/group/(?P<group_id>\d+)/addclient/$',
        add_client_to_group_page, name="add_client_to_group_page"),
    url(r'^manage/group/create/$', create_group_page,
        name="create_group_page"),
        
    url(r'^manage/orgmap/$', manage_org_map_page,
        name="manage_org_map_page"),
        
    url(r'^setup/$', setup_page, name="setup_page"),
    url(r'^setup_complete/$', direct_to_template,
        {'template':'openvpn_userinterface/setup_complete.html'},
        name="setup_complete_page"),
)
