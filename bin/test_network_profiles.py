#!/usr/bin/env python
# encoding: utf-8
# vim: shiftwidth=4 expandtab

from pprint import pprint
from openvpnweb.openvpn_userinterface.models import (NetworkProfile,
    ProfileInheritance)

def test_network_profiles():
    base = NetworkProfile(name="Base Profile")
    base.save()
    base.set_attribute("vlan","1")
    base.set_attribute("dns","130.230.4.2")

    example = NetworkProfile(name="Example Profile")
    example.save()

    example.inherit(base)
    example.set_attribute("vlan", "2")
    example.set_attribute("network_id", "130.230.1.0")
    example.set_attribute("netmask", "255.255.255.0")
    example.set_attribute("gateway", "130.230.1.1")
    
    example2 = NetworkProfile(name="Another Example Profile")
    example2.save()
    
    example2.inherit(base)
    example2.set_attribute("vlan","3")
    
    multiple_inheritance = NetworkProfile(name="Multiple Inheritance Example")
    multiple_inheritance.save()
    
    multiple_inheritance.inherit(example, priority=1)
    multiple_inheritance.inherit(example2, priority=0)
    
    circular_inheritance = NetworkProfile(name="Circular Inheritance Example")
    circular_inheritance.save()
    
    circular_inheritance2 = NetworkProfile(name="Circular Inheritance Example 2")
    circular_inheritance2.save()
    
    circular_inheritance.inherit(circular_inheritance2)
    circular_inheritance2.inherit(circular_inheritance)

    return multiple_inheritance, circular_inheritance

if __name__ == "__main__":
    m, c = test_network_profiles()
    pprint(m.attributes)
    pprint(c.attributes) # should raise CircularInheritance