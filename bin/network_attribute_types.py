#!/usr/bin/env python
# encoding: utf-8
# vim: shiftwidth=4 expandtab

from openvpnweb.openvpn_userinterface.models import NetworkAttributeType

IP_RE = r"\d+\.\d+\.\d+\.\d+"

TYPES = [
    ("vlan", "VLAN number", r"\d+", False),
    ("network_id", "Network address", IP_RE, False),
    ("netmask", "Subnet mask", IP_RE, False),
    ("gateway", "Default gateway", IP_RE, False),
    ("dns", "Name server", IP_RE, True),
    ("route", "Route", "", True),
]

def install_network_attribute_types():
    for name, description, regex, multiple in TYPES:
        NetworkAttributeType(
            name=name,
            description=description,
            regex=regex,
            multiple=multiple
        ).save()

if __name__ == "__main__":
    install_network_attribute_types()
