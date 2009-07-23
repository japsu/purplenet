from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import (HttpResponseForbidden, HttpResponseRedirect,
    HttpResponseNotAllowed, HttpResponse)

from openvpnweb.openvpn_userinterface.models import (Org, Network,
    ClientCertificate)

from certlib import openssl
from datetime import datetime, timedelta
from cStringIO import StringIO

import zipfile

@login_required
def order_page(request, org_id, network_id):
    org = get_object_or_404(Org, id=int(org_id))
    network = get_object_or_404(Network, id=int(network_id))

    if request.method == 'POST':
        client = request.session["client"]

        if not org in client.orgs:
            return HttpResponseForbidden()

        if not org in network.orgs_that_have_access_set.all():
            return HttpResponseForbidden()

        common_name = org.get_random_cn()
        ca = org.client_ca
        config = ca.config
        chain_dir = settings.OPENVPNWEB_OPENSSL_CHAIN_DIR
        server_ca_crt = network.server_ca.get_ca_certificate_path()
        
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

        pkcs12 = openssl.create_pkcs12(
            crt=crt,
            key=key,
            chain_dir=chain_dir,
            extra_crt_path=server_ca_crt
        )

        response = HttpResponse(mimetype='application/zip')
        response['Content-Disposition'] = 'filename=openvpn-certificates.zip'

        # TODO with ZipFile(...) as zip?
        # TODO write directly into response?
        buffer=StringIO()
        zip = zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED)
        zip.writestr("keys.p12", pkcs12)
        zip.close()
        buffer.flush()
        ret_zip = buffer.getvalue()
        buffer.close()
        response.write(ret_zip)

        return response

    elif request.method == "GET":
        return post_confirmation_page(request,
            question="Order a certificate for {0}?".format(network),
            choices=[
                ("Order", reverse("order_page",
                    kwargs=dict(network_id=network_id, org_id=org_id))),
                ("Cancel", reverse("main_page"))
            ]
        )

    else:
        return HttpResponseNotAllowed()

