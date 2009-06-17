from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',

#URLs for  user interface
(r'^', include('openvpnweb.openvpn_userinterface.urls')),

# URL for admin interface:
(r'^admin/(.*)', admin.site.root),

)
