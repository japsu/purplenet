# vim: shiftwidth=4 expandtab

from django.conf.urls.defaults import *
from openvpnweb.openvpn_userinterface.views import *

urlpatterns = patterns('',
    url(r'^$', main_page, name="main_page"),
    url(r'^login/$', login_page, name="login_page"),
    url(r'^revoke/(?P<cert_id>\d+)$', revoke_page, name="revoke_page"),
    url(r'^order/(?P<org_id>\d+)/(?P<network_id>\d+)$', order_page,
        name="order_page"),
    url(r'^logout/$', logout_page, name="logout_page"),
    url(r'^manage/log/$', manage_log_page, name="manage_log_page"),
    url(r'^manage/$', manage_page, name="manage_page"),
    url(r'^manage/server/(?P<server_id>\d+)/$', manage_server_page,
        name="manage_server_page"),
    url(r'^manage/network/(?P<org_id>\d+)/(?P<network_id>\d+)/$',
        manage_network_page, name="manage_network_page"),
    url(r'^manage/org/(?P<org_id>\d+)/$', manage_org_page,
        name="manage_org_page"),
    url(r'^manage/client/(?P<client_id>\d+)/$', manage_client_page,
        name="manage_client_page"),
    url(r'^manage/group/(?P<group_id>\d+)$', manage_group_page,
        name="manage_group_page"),
    url(r'^manage/group/(?P<group_id>\d+)/removeclient/(?P<client_id>\d+)$',
        remove_client_from_group_page, name="remove_client_from_group_page"),
    url(r'^setup/$', setup_page, name="setup_page"),
)
