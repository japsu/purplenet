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
The certificate revokation view.
"""

from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.views.decorators.http import require_POST
from django.http import (HttpResponseForbidden, HttpResponseRedirect,
    HttpResponseNotAllowed)

from purplenet.openvpn_userinterface.models import ClientCertificate

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
