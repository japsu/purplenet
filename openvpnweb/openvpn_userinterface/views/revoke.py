# encoding: utf-8
# vim: shiftwidth=4 expandtab

from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.views.decorators.http import require_POST
from django.http import (HttpResponseForbidden, HttpResponseRedirect,
    HttpResponseNotAllowed)

from openvpnweb.openvpn_userinterface.models import ClientCertificate

from .helpers import post_confirmation_page
from ..logging import log

@login_required
@require_POST
def revoke_page(request, cert_id):   
    certificate = get_object_or_404(ClientCertificate, id=int(cert_id))
    org = certificate.org
    client = request.session["client"]

    if not client.may_revoke(certificate):
        log(
            event="client_certificate.revoke",
            denied=True,
            client=client,
            group=org.group,
            network=certificate.network,
            client_certificate=certificate
        )
        return HttpResponseForbidden()

    certificate.revoke(revoked_by=client)
    certificate.save()

    log(
        event="client_certificate.revoke",
        client=client,
        group=org.group,
        network=certificate.network,
        client_certificate=certificate
    )

    return_url = request.META.get("HTTP_REFERER", reverse("main_page"))
    return HttpResponseRedirect(return_url)
