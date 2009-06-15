from django.conf.urls.defaults import *
from openvpnweb.openvpn_userinterface.views import *

urlpatterns = patterns('',

#URLs for  user interface
(r'^$', login_page),
(r'^main/$', main_page),
(r'^revoke/$', revoke_page),
(r'^order/$', order_page),
(r'^download/$', download),
(r'^logout/$', logout_page),

)
