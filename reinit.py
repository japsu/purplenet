#!/usr/bin/env python
# coding: utf-8
# vim: shiftwidth=4 expandtab  

print """
##############################################################################
# BIG UGLY WARNING CONCERNING reinit.py!
##############################################################################
# This script is for internal development and testing only. It will create
# user accounts with weak and/or known passwords and contains hard-coded
# absolute paths that will not work in your system. Please do not run it
# against your database unless you know what you are doing.
##############################################################################
"""

from os import environ as env
env["DJANGO_SETTINGS_MODULE"] = "openvpnweb.settings"

from openvpnweb.openvpn_userinterface.models import *
from django.contrib.auth.models import User, Group

from datetime import datetime

superuser = User(
    username="pajukans",
    is_staff=True,
    is_superuser=True,
    password="sha1$aadcf$d4b51905abd1958fd4568e223cf2c5ff560867e1"
)
superuser.save()

group = Group(
    name="TTY"
)
group.save()

user = User(
    username="testuser"
)
user.set_password('weak_password')
user.save()

user.groups.add(group)
user.save()

root_ca_cert = CACertificate(
    common_name="RootCA",
    ca=None,                    # the root is self- or externally signed
    granted=datetime.now()     # XXX
)
root_ca_cert.save()

root_ca = IntermediateCA(
    config="/home/pajukans/Temp/testca/RootCA/openssl.cnf",
    owner=None,                 # to be filled later on
    certificate=root_ca_cert
)    
root_ca.save()

server_ca_cert = CACertificate(
    common_name="ServerCA",
    ca=root_ca,
    granted=datetime.now()
)
server_ca_cert.save()

server_ca = ServerCA(
    config="/home/pajukans/Temp/testca/ServerCA/openssl.cnf",
    owner=None,                 # to be filled later on
    certificate=server_ca_cert
)
server_ca.save()

client_ca_cert = CACertificate(
    common_name="ClientCA",
    ca=root_ca,
    granted=datetime.now()
)
client_ca_cert.save()

client_ca = IntermediateCA(
    config="/home/pajukans/Temp/testca/ClientCA/openssl.cnf",
    owner=None,
    certificate=client_ca_cert
)
client_ca.save()

dept_ca_cert = CACertificate(
    common_name="DeptCA",
    ca=client_ca,
    granted=datetime.now()
)
dept_ca_cert.save()

dept_ca = ClientCA(
    config="/home/pajukans/Temp/testca/DeptCA/openssl.cnf",
    owner=None,
    certificate=dept_ca_cert
)
dept_ca.save()

org = Org(
    group=group,
    client_ca=dept_ca,
    cn_suffix=".rd.tut.fi"
)
org.save()

for ca in (root_ca, server_ca, client_ca, dept_ca):
    ca.owner = org
    ca.save()

server_cert = ServerCertificate(
    common_name="testserver.rd.tut.fi",
    ca=server_ca,
    granted=datetime.now()
)
server_cert.save()
    
server = Server(
    name="testserver",
    address="10.0.0.1",
    port=1194,
    protocol="udp",
    mode="routed",
    certificate=server_cert
)
server.save()

network = Network(
    name="testnet",
    org=org,
    server_ca=server_ca
)
network.save()

network.server_set.add(server)
network.save()
