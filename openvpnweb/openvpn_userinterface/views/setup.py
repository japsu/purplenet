# encoding: utf-8
# vim: shiftwidth=4 expandtab

from django.contrib.formtools.wizard import FormWizard
from datetime import datetime, timedelta

from openvpnweb.openvpn_userinterface.forms import *

__all__ = ["setup_wizard"]

SETUP_WIZARD_FORM_LIST = [
    CAForm,
    OrgForm,
    OrgMapForm,
    ServerForm,
    NetworkForm
]

def create_ca(common_name, ca, dir, ca_cls):
    # XXX
    now = datetime.now()
    then = now + timedelta(days=3650)

    new_ca_cert = CACertificate(
        common_name=common_name,
        ca=ca,
        granted=now,
        expires=then
    )
    new_ca = IntermediateCA(
        dir=dir,
        owner=None,
        certificate=new_ca_cert
    )

    new_ca.create_ca_files()
    new_ca_cert.save()
    new_ca.save()

    return new_ca

def parse_org_map(org_map, org):
    data = json.loads(org_map)
    for mapping_data in data:
        org = Org.objects.get(name=mapping_data["obj"])
    
        mapping = OrgMapping(org=org)
        mapping.save()

        for element_data in mapping_data["elements"]:
            type = MappingType.objects.get_or_create(
                namespace=element_data["namespace"],
                source_name=element_data["source_name"],

                defaults=dict(
                    name="%s (%s)" % (source_name, namespace),
                    description="Automatically created by parse_org_map"
                )
            )

            element = MappingElement(
                type=type,
                mapping=mapping,
                value=element_data["value"]
            )
            element.save()

def setup_complete(request, ca_form, org_form, org_map_form, server_form,
        network_form):
    
    # CREATE THE CA HIERARCHY

    # Root CA
    root_ca = create_ca(
        ca_form.cleaned_data["root_ca_cn"],
        None,
        ca_form.cleaned_data["root_ca_dir"],
        IntermediateCA
    )

    # Server CA
    server_ca = create_ca(
        ca_form.cleaned_data["server_ca_cn"],
        root_ca,
        ca_form.cleaned_data["server_ca_dir"],
        ServerCA
    )

    # Client CA
    client_ca = create_ca(
        ca_form.cleaned_data["client_ca_cn"],
        root_ca,
        ca_form.cleaned_data["client_ca_dir"],
        IntermediateCA
    )

    # CREATE THE ORGANIZATION AND ITS GROUPS

    org_name = org_form.cleaned_data["org_name"]

    # User group
    group = Group(name=org_name)
    group.save()

    # Admin group
    admin_group = Group(name=org_name + " (Admin)")
    admin_group.save()

    # Orgazinational client CA
    dept_ca = create_ca(
        org_name + " Client CA", # XXX
        client_ca,
        org_form.cleaned_data["ca_dir"]
    )

    # Organization object
    org = Org(
        group=group,
        cn_suffix=org_form.cleaned_data["cn_suffix"]
    )
    org.save()

    # Set the admin group
    org.admin_group_set.add(admin_group)
    org.save()

    # Set the ownership of the CAs
    for ca in (root_ca, server_ca, client_ca, dept_ca):
        ca.owner = org
        ca.save()

    # CREATE THE ORG MAP
    parse_org_map(server_form.cleaned_data["org_map"], org=org)

    # CREATE THE SERVER AND ITS CERTIFICATE

    # Server certificate
    server_cert = ServerCertificate(
        common_name=server_form.cleaned_data["server_cn"],
        ca=server_ca,
        granted=datetime.now(),
        expires=datetime.now() + timedelta(days=365)
    )
    server_cert.create_files()
    server_cert.save()

    # Server
    server = server_form.save()
    server.certificate = server_cert
    server.save()

    # CREATE A NETWORK

    network = Network(
        name=network_form.cleaned_data["network_name"],
        owner=org,
        server_ca=server_ca
    )
    network.save()

    network.orgs_that_have_access_set.add(org)
    network.server_set.add(server)
    network.save()

    return render_to_response("openvpn_userinterface/setupcomplete.html",
        RequestContext(request, {}))

class SetupWizard(FormWizard):
    def done(self, request, form_list):
        setup_complete(request, *form_list)

    def get_template(self, step):
        return "openvpn_userinterface/setupwizard.html"

setup_wizard = SetupWizard(SETUP_WIZARD_FORM_LIST)
