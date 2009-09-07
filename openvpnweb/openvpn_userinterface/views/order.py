from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import (HttpResponseForbidden, HttpResponseRedirect,
    HttpResponseNotAllowed, HttpResponse)

from ..models import Org, Network, ClientCertificate, SiteConfig
from ..logging import log

from certlib import openssl
from datetime import datetime, timedelta
from cStringIO import StringIO

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

        if not client.may_access(org, network):
            log(
                event="client_certificate.create",
                denied=True,
                client=client,
                group=org.group,
                network=network
            )

        common_name = org.get_random_cn()
        ca = org.client_ca
        config = ca.config
        chain_dir = siteconfig.copies_dir
        server_ca_crt = siteconfig.server_ca.get_ca_certificate_path()
        
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
        
        client_config = network.client_config

        response = HttpResponse(mimetype='application/zip')
        response['Content-Disposition'] = 'filename=openvpn-certificates.zip'

        # TODO with ZipFile(...) as zip?
        # TODO write directly into response?
        buffer=StringIO()
        zip = zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED)
        _zip_write_file(zip, "keys.p12", pkcs12)
        _zip_write_file(zip, "openvpn.conf", client_config)
        zip.close()
        buffer.flush()
        ret_zip = buffer.getvalue()
        buffer.close()
        response.write(ret_zip)

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

