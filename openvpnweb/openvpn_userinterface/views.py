# vim: shiftwidth=4 expandtab

from django.shortcuts import render_to_response
from django.http import Http404, HttpResponseRedirect, HttpResponse
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
                except:
                    #luodaan client ja taman jalkeen katsotaan mihin grouppiin
                    #on oikeudet ja luodaan nekin.
                    client = Client(name=user.username)
                    client.save()
                 
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
def order_page(request):
    if request.method == 'POST':
        try:
            cert_id = request.session["cert_id"]
            return HttpResponseRedirect(
                reverse("openvpnweb.openvpn_userinterface.views.main_page"))
        except:
            pass
        client = request.session["client"]
        organisations = request.session["organisations"]
        network_id = request.POST['net_id']
        # XXX
        try:
            network = Network.objects.get(id = network_id)
        except:
            pass
        if network.org in organisations:
            common_name = generate_random_string() + network.org.cn_suffix
            ca = network.org.ca
            config = ca.config
            
            # TODO user-supplied CSR
            key = openssl.generate_rsa_key(config=config)
            csr = openssl.create_csr(common_name=common_name, key=key, config=config)
            cert = openssl.sign_certificate(csr, config=config)

            certificate = Certificate()
            certificate.common_name = common_name
            certificate.ca = ca
            certificate.timestamp = datetime.now()
            certificate.user = client
            certificate.network = network
            certificate.save()

            # FIXME If the user orders multiple certificates without downloading them in between, catastrophe happens.
            # The session data might not be the right place for this kind of information.
            # Possible solution: Make the user download the certificate right away after it has been created.
            request.session["new_key"] = key
            request.session["new_cert"] = cert
            request.session["new_cert_pk"] = certificate.pk
        else:
            # XXX
            raise AssertionError("Then what?")
    return HttpResponseRedirect(
        reverse("openvpnweb.openvpn_userinterface.views.main_page"))

@login_required
def download(request):
    # XXX
    try:
        key = request.session["new_key"]
        cert = request.session["new_cert"]
        cert_pk = request.session["new_cert_pk"]
        certificate = Certificate.objects.get(pk=cert_pk)
        if certificate.downloaded:
            raise Exception()
    except:
        return HttpResponseRedirect(
            reverse("openvpnweb.openvpn_userinterface.views.main_page"))

    del request.session["new_key"]
    del request.session["new_cert"]
    del request.session["new_cert_pk"]

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

@login_required
def revoke_page(request):
    if request.method == 'POST':
	cert_id_p = None

        # XXX
	try:
            cert_id_p = request.POST['cert_id']

	    cert_id_s = None

            # XXX
	    try:
		cert_id_s = request.session['cert_id']
	    except:
		pass

	    if not cert_id_s is None and cert_id_p != cert_id_s:
                return HttpResponseRedirect(reverse(
                    "openvpnweb.openvpn_userinterface.views.main_page"))

            client = request.session["client"]
        except:
	    return HttpResponseRedirect(reverse(
                "openvpnweb.openvpn_userinterface.views.main_page"))

	cert_id = cert_id_p
	certificate = None
        # XXX
        try:
            certificate = Certificate.objects.get(id = cert_id)

            # XXX 
	    if certificate.revokated:
		return HttpResponseRedirect(reverse(
                    "openvpnweb.openvpn_userinterface.views.main_page"))

        except:
            pass
        certificates = client.certificate_set.all()
        
        if certificate in certificates:
            revoke_certificate(certificate.ca_name, certificate.common_name)
            certificate.revoked = True
            certificate.timestamp = datetime.now()
	    certificate.downloaded = True
            certificate.save()

            # XXX
            try:
                del request.session["path"]
                del request.session["cert_id"]
            except:
                pass
    return HttpResponseRedirect(reverse(
        "openvpnweb.openvpn_userinterface.views.main_page"))

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
