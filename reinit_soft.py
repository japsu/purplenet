from django.conf import settings

import httplib
import urllib
from contextlib import closing

OPENVPNWEB_HOST="localhost"
OPENVPNWEB_SETUP_PATH="/openvpn/setup"

def reinit_soft():
    params = {
        "setup_key" : settings.OPENVPNWEB_SETUP_KEY,
        "ca_dir" : "/home/pajukans/Temp/testfoo",
        "root_ca_cn": "Root CA",
        "server_ca_cn": "Server CA",
        "client_ca_cn": "Client CA",
        "superuser_name": "Superuser",
        "password": "super_weak_password",
        "password_again": "super_weak_password",
    }
    post_data = urllib.urlencode(params)
    
    headers = { "Content-Type" : "application/x-www-form-urlencoded" }
    
    with closing(httplib.HTTPConnection(OPENVPNWEB_HOST)) as conn:
        conn.request("POST", OPENVPNWEB_SETUP_PATH, post_data, headers)
        response = conn.getresponse()
        status, reason = response.status, response.reason
        data = response.read()
    
    