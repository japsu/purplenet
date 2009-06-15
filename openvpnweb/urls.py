from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',

#URLs for  user interface
(r'^openvpn/', include('openvpnweb.openvpn_userinterface.urls')),

# URL for admin interface:
(r'^openvpn/admin/(.*)', admin.site.root),

)
