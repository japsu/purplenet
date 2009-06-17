from openvpnweb.openvpn_userinterface.models import *
from django.contrib import admin

admin.site.register(CertificateAuthority)
admin.site.register(Org)
admin.site.register(Client)
admin.site.register(Server)
admin.site.register(Network)
admin.site.register(NetworkAttribute)
admin.site.register(Certificate)
