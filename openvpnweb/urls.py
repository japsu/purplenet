from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',

#URLs for  user interface
(r'^openvpn/', include('openvpn.openvpn_userinterface.urls')),

# URL for admin interface:
(r'^openvpn/admin/(.*)', admin.site.root),

)
