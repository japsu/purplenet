# encoding: utf-8
# vim: shiftwidth=4 expandtab

from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import (HttpResponseForbidden, HttpResponseRedirect,
    HttpResponseNotAllowed)

from openvpnweb.openvpn_userinterface.models import ClientCertificate

from .helpers import post_confirmation_page
from ..logging import log

@login_required
def revoke_page(request, cert_id):
    if request.method not in ("GET", "POST"):
        return HttpMethodNotAllowed(["GET", "POST"])    

    certificate = get_object_or_404(ClientCertificate, id=int(cert_id))
    org = certificate.org

    if request.method == 'POST':
        client = request.session["client"]
        if not client.may_revoke(certificate):
            log(
                event="client_certificate.revoke",
                denied=True,
                client=client,
                group=org.group,
                client_certificate=certificate
            )
            return HttpResponseForbidden()

        certificate.revoke(revoked_by=client)
        certificate.save()

        log(
            event="client_certificate.revoke",
            client=client,
            group=org.group,
            client_certificate=certificate
        )

        return HttpResponseRedirect(reverse("main_page"))

    else: # request.method == 'GET'
        if not client.may_revoke(certificate):
            return post_confirmation_page(request,
                question="You may not revoke certificate {0}.",
                choices=[
                    ("Return", reverse("main_page"))
                ]
            )
        else:
            return post_confirmation_page(request,
                question="Really revoke certificate {0}?".format(certificate),
                choices=[
                    ("Revoke", reverse("revoke_page", kwargs=
                        dict(cert_id=cert_id))),
                    ("Cancel", reverse("main_page"))
                ]
            )

