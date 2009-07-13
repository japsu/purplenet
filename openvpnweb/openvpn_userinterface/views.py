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
from openvpnweb.access_control import manager_required

import certlib.openssl as openssl

from datetime import datetime
import zipfile
from cStringIO import StringIO
from collections import defaultdict

# XXX
DEFAULT = "TTY"

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
    #if user.is_authenticated:
    #    return HttpResponseRedirect('/openvpn/openvpn/main/')
    variables = {
        'type': "info", 
        'message_login': ""
    }
    if request.method == 'POST':
	# XXX
        # if request.session.test_cookie_worked():
        #    request.session.delete_test_cookie()
        # else:
        #    variables = {
        #        'type': "error",
        #        'message_login': "Please enable cookies and try again!"
        #    }
        #    return render_to_response('openvpn_userinterface/login.html',
        #        variables )

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
                    #luodaan client ja taman jalkeen katsotaan mihin grouppiin
                    #on oikeudet ja luodaan nekin.
                    client = Client(user=user)
                    client.save()
                 
                # XXX
                #if not DEFAULT in ["%s" % g for g in user.groups.all()]:
                #    g = Group.objects.get(name=DEFAULT)
                #    user.groups.add(g)
                #    user.save()
                    
                #groups = user.groups.all()
                #organisations = []
                #for group in groups:
                #    try:
                #  	organisations.append(Org.objects.get(name=group.name))
                #    except Org.DoesNotExist:	
                #  	pass
                
                # XXX
                request.session["organisations"] = list(client.orgs.all())
                request.session["client"] = client
                
		return HttpResponseRedirect(reverse(main_page))
        else:
            variables = {
               'type' : "error", 
               'message_login' : "Your login details are incorrect. " +
                    "Please try again."
            }
                          
    request.session.set_test_cookie()
    return render_to_response('openvpn_userinterface/login.html',variables)
                
@login_required
def main_page(request):
    
    client = request.session["client"]
    organisations = request.session["organisations"]
    
    # XXX try to replace with smarter queries
    certificates = defaultdict(list)
    for cert in client.certificate_set.all():
        network = cert.network
        certificates[network.id].append(cert)

    variables = RequestContext(request, {
        'client': client,
        'organisations': organisations,
        'certificates': certificates,
    })
    
    return render_to_response(
        'openvpn_userinterface/main_page.html', variables 
    )

@login_required
def order_page(request, network_id):
    network = get_object_or_404(Network, id=int(network_id))

    if request.method == 'POST':
        client = request.session["client"]
        organisations = request.session["organisations"]

        if not network.org in organisations:
            return HttpResponseForbidden()

        common_name = network.org.get_random_cn()
        ca = network.org.client_ca
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
                    kwargs=dict(network_id=network_id))),
                ("Cancel", reverse("main_page"))
            ]
        )

    else:
        return HttpResponseNotAllowed()

@login_required
def revoke_page(request, cert_id):
    certificate = get_object_or_404(Certificate, id=int(cert_id))

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
    # XXX
    try:
        del request.session["client"]
        del request.session["organisations"]
    except:
        pass
    
    logout(request)
    return HttpResponseRedirect(reverse(
        "openvpnweb.openvpn_userinterface.views.login_page"))        

@manager_required
def manage_page(request):
    manager = session["client"]
    organizations = manager.get_managed_organizations()

    vars = { "organizations" : organizations }
    return render_to_response("openvpn_userinterface/manage.html", {})

@manager_required
def manage_org_page(request, org_id):
    org = get_object_or_404(Org, org_id=int(org_id))
    manager = session["client"]
    clients = org.client_set.all()

    if not manager.may_manage(org):
        return HttpResponseForbidden()

    vars = { "clients" : clients }
    return render_to_response("openvpn_userinterface/manage_org.html", vars)
