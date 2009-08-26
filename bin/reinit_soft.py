#!/usr/bin/env python
# encoding: utf-8
# vim: shiftwidth=4 expandtab

from __future__ import with_statement

from django.conf import settings

import httplib
import urllib
from contextlib import closing

try:
    import BeautifulSoup
except ImportError:
    pass

OPENVPNWEB_HOST="localhost"
OPENVPNWEB_SETUP_PATH="/openvpn/setup/"

def mangle(data):
    try:
        bs = BeautifulSoup
    except NameError:
        return data
    
    soup = bs.BeautifulSoup(data)
    return str(soup.find("title"))

def reinit_soft():
    params = {
        "setup_key" : settings.OPENVPNWEB_SETUP_KEY,
        "ca_dir" : "/home/pajukans/Temp/testca",
        "root_ca_cn": "Root CA",
        "server_ca_cn": "Server CA",
        "client_ca_cn": "Client CA",
        "superuser_name": "Superuser",
        "password": "super_weak_password",
        "password_again": "super_weak_password",
    }
    post_data = urllib.urlencode(params)
    
    headers = {
        "Content-Type" : "application/x-www-form-urlencoded"
    }
    
    with closing(httplib.HTTPConnection(OPENVPNWEB_HOST)) as conn:
        conn.request("POST", OPENVPNWEB_SETUP_PATH, post_data, headers)
        response = conn.getresponse()
        status, reason = response.status, response.reason
        data = response.read()
    
    print status, reason, mangle(data)
    
if __name__== "__main__":
    reinit_soft()