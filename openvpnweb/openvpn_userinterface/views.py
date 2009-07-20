# vim: shiftwidth=4 expandtab

from django.shortcuts import render_to_response, get_object_or_404
from django.http import (HttpResponseRedirect, HttpResponse,
    HttpResponseForbidden, HttpResponseNotAllowed)
from django.contrib.auth.models import User, Group
from django.contrib.auth import logout, authenticate, login
from django.template import Context, RequestContext
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.conf import settings

from openvpnweb.openvpn_userinterface.models import *
from openvpnweb.settings import LOGIN_URL
from openvpnweb.helper_functions import *
from openvpnweb.access_control import (manager_required,
    update_group_membership)

import certlib.openssl as openssl

from datetime import datetime
import zipfile
from cStringIO import StringIO
from collections import defaultdict

# XXX
#DEFAULT = "TTY"

def post_confirmation_page(request, question, choices):
    """post_confirmation_page(request, question, choices) -> response

    A helper for implementing the lo-REST protocol. Should a POST-only resource
    be accessed with the GET method, this method may be used to return a
    confirmation page that allows the user to retry with the POST method or
    cancel.
    """

    client = request.session.get("client", None)

    vars = {
        "question" : question,
        "choices" : choices,
        "client" : client,
    }
    return render_to_response("openvpn_userinterface/confirmation.html", vars)

def login_page(request):
    vars = {
        'type': "info", 
        'message_login': ""
    }

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)    
                client = None
                try:
                    client = Client.objects.get(user=user)
                except Client.DoesNotExist:
                    client = Client(user=user)
                    client.save()
                 
                if settings.OPENVPNWEB_USE_GROUP_MAPPINGS:
                    update_group_membership(client)
                    client.save()

                # XXX
                request.session["client"] = client
                
		return HttpResponseRedirect(reverse(main_page))
        else:
            vars = RequestContext(request, {
               'type' : "error", 
               'message_login' : "Your login details are incorrect. " +
                    "Please try again."
            })
                          
    request.session.set_test_cookie()
    return render_to_response('openvpn_userinterface/login.html',vars)
                
@login_required
def main_page(request):
    
    client = request.session["client"]
    
    # XXX try to replace with smarter queries
    data = []
    for org in client.orgs.all():
        networks = []
        for net in org.accessible_network_set.all():
            certificates = ClientCertificate.objects.filter(
                network=net,
                ca__owner__exact=org,
                owner=client
            )
            networks.append((net, certificates))
        data.append((org, networks))

    variables = RequestContext(request, {
        'data': data,
        'client': client,
    })
    
    return render_to_response(
        'openvpn_userinterface/main_page.html', variables 
    )

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
            granted=datetime.now(),
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

@login_required
def revoke_page(request, cert_id):
    certificate = get_object_or_404(ClientCertificate, id=int(cert_id))

    if request.method == 'POST':
        client = request.session["client"]
        if not client.may_revoke(certificate):
            return HttpResponseForbidden()

        certificate.revoke()
        certificate.save()
        return HttpResponseRedirect(reverse("main_page"))

    elif request.method == 'GET':
        return post_confirmation_page(request,
            question="Really revoke certificate {0}?".format(certificate),
            choices=[
                ("Revoke", reverse("revoke_page", kwargs=
                    dict(cert_id=cert_id))),
                ("Cancel", reverse("main_page"))
            ]
        )

    else:
        return HttpResponseNotAllowed()

def logout_page(request):
    if request.method == "POST":
        try:
            del request.session["client"]
        except KeyError, e:
            pass
        
        logout(request)
        return HttpResponseRedirect(reverse(
            "openvpnweb.openvpn_userinterface.views.login_page"))
    elif request.method == "GET":
        return post_confirmation_page(request,
            question="Really log out?",
            choices=[
                ("Log out", reverse("logout_page")),
                ("Cancel", reverse("main_page"))
            ]
        )

    else:
        return HttpResponseNotAllowed()

@manager_required
def manage_page(request):
    client = request.session["client"]

    vars = RequestContext(request, {
        "client" : client
    })
    return render_to_response("openvpn_userinterface/manage.html", vars)

@manager_required
def manage_org_page(request, org_id):
    org = get_object_or_404(Org, org_id=int(org_id))
    client = session["client"]
    clients = org.client_set.all()

    if not client.may_manage(org):
        return HttpResponseForbidden()

    vars = RequestContext(request, {
        "client" : client,
        "clients" : clients,
    })
    return render_to_response("openvpn_userinterface/manage_org.html", vars)
