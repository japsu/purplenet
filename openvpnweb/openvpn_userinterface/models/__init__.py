# encoding: utf-8
# vim: shiftwidth=4 expandtab

# FIXME There's been dragons before, but this time they've gotten serious.
#
# This is a hack to work around Django's braindead way of finding models.
# Basically manage.py fails to find our modules at initialize time if we
# don't force them in the openvpnweb.openvpn_userinterface.models namespace
# the hard way.
#
# This neat little trick is simplified from
# http://www.ifisgeek.com/2009/01/26/splitting-django-models-into-separate-files/
# that presents the way Google does it.
#
# Once Django fixes their support for models in multiple files per app,
# uncomment the commented imports below and delete everything after
# the "XXX BEGIN DRAGONS".

#from .ca import CertificateAuthority, IntermediateCA, ClientCA, ServerCA
#from .certificates import (Certificate, ClientCertificate, ServerCertificate,
#    CACertificate)
#from .client import Client
#from .logging import LogEntry
#from .network import (NetworkProfile, NetworkAttribute, NetworkAttributeType,
#    Network)
#from .org import Org
#from .org_map import (OrgMapping, MappingType, MappingElement)
#from .server import Server

# XXX BEGIN DRAGONS

from certlib.helpers import import_module

DRAGON_LORE = [
    ("openvpnweb.openvpn_userinterface.models.ca", [ 
        "CertificateAuthority",
        "IntermediateCA",
        "ClientCA",
        "ServerCA",
    ]),
    
    ("openvpnweb.openvpn_userinterface.models.certificates", [ 
        "Certificate",
        "ClientCertificate",
        "ServerCertificate",
        "CACertificate",
    ]),

    ("openvpnweb.openvpn_userinterface.models.client", [ 
        "Client",
    ]),

    ("openvpnweb.openvpn_userinterface.models.logging", [ 
        "LogEntry",
    ]),

    ("openvpnweb.openvpn_userinterface.models.network", [ 
        "NetworkProfile",
        "NetworkAttribute",
        "NetworkAttributeType",
        "Network",
    ]),

    ("openvpnweb.openvpn_userinterface.models.org", [ 
        "Org",
    ]),

    ("openvpnweb.openvpn_userinterface.models.org_map", [ 
        "OrgMapping",
        "MappingType",
        "MappingElement",
    ]),

    ("openvpnweb.openvpn_userinterface.models.server", [ 
        "Server",
    ]),
]

final_names = []
for module_name, model_names in DRAGON_LORE:
    module = import_module(module_name)
    for model_name in model_names:
        model = getattr(module, model_name)
        exec "%s = model" % model_name
    final_names.extend(model_names)

__all__ = final_names
