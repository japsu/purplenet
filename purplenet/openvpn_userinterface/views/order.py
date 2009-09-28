# encoding: utf-8
# vim: shiftwidth=4 expandtab
#
# PurpleNet - a Web User Interface for OpenVPN
# Copyright (C) 2009  Santtu Pajukanta
# Copyright (C) 2008, 2009  Tuure Vartiainen, Antti Niemelä, Vesa Salo
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
The certificate download view.
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import (HttpResponseForbidden, HttpResponseRedirect,
    HttpResponseNotAllowed, HttpResponse)

from ..models import Org, Network, ClientCertificate, SiteConfig
from ..logging import log

from libpurplenet import openssl
from datetime import datetime, timedelta
from cStringIO import StringIO
from contextlib import closing

import zipfile

def _zip_write_file(zip, filename, contents, mode=0666):
    info = zipfile.ZipInfo(filename)
    info.external_attr = mode << 16L
    zip.writestr(info, contents)

@login_required
def order_page(request, org_id, network_id):
    org = get_object_or_404(Org, id=int(org_id))
    network = get_object_or_404(Network, id=int(network_id))
    siteconfig = SiteConfig.objects.get()

    if request.method == 'POST':
        client = request.session["client"]
        
        client_san = client.sanitized_name
        network_san = network.sanitized_name

        if not client.may_access(org, network):
            log(
                event="client_certificate.create",
                denied=True,
                client=client,
                group=org.group,
                network=network
            )

        common_name = "%s-%s" % (client_san, org.get_random_cn())
        ca = org.client_ca
        config = ca.config
        chain_dir = siteconfig.copies_dir
        server_ca_crt = siteconfig.server_ca.get_ca_certificate_path()
        
        # Generate keys
        # TODO user-supplied CSR
        key = openssl.generate_rsa_key(config=config)
        csr = openssl.create_csr(common_name=common_name, key=key,
            config=config)
        # TODO certificate_authority.sign(csr)
        crt = openssl.sign_certificate(csr, config=config)

        certificate = ClientCertificate(
            common_name=common_name,
            ca=ca,
            granted=datetime.now(), #XXX this should come from the cert data
            expires=datetime.now() + timedelta(days=365), # XXX this too
            network=network,
            owner=client
        )
        certificate.save()

        log(
            event="client_certificate.create",
            client=client,
            group=org.group,
            network=network,
            client_certificate=certificate
        )

        pkcs12 = openssl.create_pkcs12(
            crt=crt,
            key=key,
            chain_dir=chain_dir,
            extra_crt_path=server_ca_crt
        )
        
        # Define file names
        
        # Assuming a user called "FooGrande" and network "PurpleNet VLAN 721",
        # the resulting file name for the key/config archive is
        # "foogrande-purplenetvlan721.zip". 
        
        filename_base = "%s-%s" % (client_san, network_san)
        keys_filename = filename_base + ".p12"
        config_filenames = (filename_base + ".ovpn", filename_base + ".conf")
        
        client_config = network.client_config(keys_filename=keys_filename)

        # Start the response, stating it's a zip file with a specific filename
        response = HttpResponse(mimetype='application/zip')
        response['Content-Disposition'] = 'filename=%s.zip' % filename_base 

        # Write config and key files into the zip file
        with closing(zipfile.ZipFile(response, "w", zipfile.ZIP_DEFLATED)) as zip:
            _zip_write_file(zip, keys_filename, pkcs12)
            
            for config_filename in config_filenames:
                _zip_write_file(zip, config_filename, client_config)
            
        return response

    elif request.method == "GET":
        return post_confirmation_page(request,
            question="Order a certificate for %s?" % network,
            choices=[
                ("Order", reverse("order_page",
                    kwargs=dict(network_id=network_id, org_id=org_id))),
                ("Cancel", reverse("main_page"))
            ]
        )

    else:
        return HttpResponseNotAllowed()

