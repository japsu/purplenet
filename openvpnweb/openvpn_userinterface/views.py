# vim: shiftwidth=4 expandtab

from django.shortcuts import render_to_response, get_object_or_404
from django.http import (HttpResponseRedirect, HttpResponse,
    HttpResponseForbidden, HttpResponseNotAllowed)
from django.contrib.auth.models import User, Group
from django.contrib.auth import logout, authenticate, login
from django.template import Context, RequestContext
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse

from openvpnweb.openvpn_userinterface.models import *
from openvpnweb.settings import LOGIN_URL
from openvpnweb.helper_functions import *

import certlib.openssl as openssl

from datetime import datetime
import zipfile
from cStringIO import StringIO
from os.path import getsize

# XXX
DEFAULT = "TTY"

def post_confirmation_page(request, question, choices):
    """post_confirmation_page(request, question, choices) -> response

    A helper for implementing the REST protocol. Should a POST-only resource
    be accessed with the GET method, this method may be used to return a
    confirmation page that allows the user to retry with the POST method or
    cancel.
    """

    vars = dict(question=question, choices=choices)
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
	if False:
		if request.session.test_cookie_worked():
		    request.session.delete_test_cookie()
		else:
		    variables = {
                        'type': "error",
		        'message_login': "Please enable cookies and try again!"
		    }
		    return render_to_response('openvpn_userinterface/login.html', variables )

        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)    
                client = None
                try:
                    client = Client.objects.get(name=user.username)
                except Client.DoesNotExist:
                    #luodaan client ja taman jalkeen katsotaan mihin grouppiin
                    #on oikeudet ja luodaan nekin.
                    client = Client(name=user.username)
                    client.save()
                 
                # XXX
                if not DEFAULT in ["%s" % g for g in user.groups.all()]:
                    g = Group.objects.get(name=DEFAULT)
                    user.groups.add(g)
                    user.save()
                    
                groups = user.groups.all()
                organisations = []
                for group in groups:
                    try:
                  	organisations.append(Org.objects.get(name=group.name))
                    except Org.DoesNotExist:	
                  	pass
                
                request.session["organisations"] = organisations
                request.session["client"] = client
                
		return HttpResponseRedirect(reverse(main_page))
        else:
            variables = {
               'type': "error", 
               'message_login': "Your login details are incorrect. Please try again."
            }
                          
    request.session.set_test_cookie()
    return render_to_response('openvpn_userinterface/login.html',variables)
                
@login_required
def main_page(request):
    
    client = request.session["client"]
    organisations = request.session["organisations"]
    
    certificates = {}
    for cert in client.certificate_set.all():
        network = cert.network
        if certificates.has_key(network.id):
	    certificates[network.id].append(cert)
        else:
            certificates[network.id] = []
	    certificates[network.id].append(cert)
    variables = RequestContext(request, {
        'client': client,
        'organisations': organisations,
        'certificates': certificates,
        'session': request.session,
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
        ca = network.org.ca
        config = ca.config
        
        # TODO user-supplied CSR
        key = openssl.generate_rsa_key(config=config)
        csr = openssl.create_csr(common_name=common_name, key=key,
            config=config)
        # TODO certificate_authority.sign(csr)
        cert = openssl.sign_certificate(csr, config=config)

        certificate = Certificate(
            common_name=common_name,
            ca=ca,
            granted=datetime.now(),
            user=client,
            network=network
        )
        certificate.save()

        response = HttpResponse(mimetype='application/zip')
        response['Content-Disposition'] = 'filename=openvpn-certificates.zip'

        # TODO with ZipFile(...) as zip?
        # TODO write directly into response?
        buffer=StringIO()
        zip = zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED)
        # TODO zip.writestr("ca.crt", server_ca)
        zip.writestr("client.key", key)
        zip.writestr("client.crt", cert)
        zip.close()
        buffer.flush()
        ret_zip = buffer.getvalue()
        buffer.close()
        response.write(ret_zip)
        certificate.downloaded = True
        certificate.save()
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
        del request.session["cert_id"]
        del request.session["path"]
    except:
        pass
    
    logout(request)
    return HttpResponseRedirect(reverse(
        "openvpnweb.openvpn_userinterface.views.login_page"))        

#def manage_page(request):
