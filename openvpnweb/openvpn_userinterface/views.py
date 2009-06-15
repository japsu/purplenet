# vim: shiftwidth=4 expandtab
# XXX hack: lots of hard-coded redirects

from django.shortcuts import render_to_response
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User, Group
from django.contrib.auth import logout, authenticate, login
from openvpn.openvpn_userinterface.models import *
from django.template import Context, RequestContext
from django.contrib.auth.decorators import login_required
from openvpn.settings import LOGIN_URL
from openvpn.certificate_manager import *
from openvpn.helper_functions import *
from datetime import datetime
import zipfile
from cStringIO import StringIO
from os.path import getsize

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
                
		return HttpResponseRedirect('/openvpn/openvpn/main/')
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
            return HttpResponseRedirect('/openvpn/openvpn/main/')
        except:
            pass
        client = request.session["client"]
        organisations = request.session["organisations"]
        network_id = request.POST['net_id']
        try:
            network = Network.objects.get(id = network_id)
        except:
            pass
        if network.org in organisations:
            common_name = generate_random_string()+network.org.cn_suffix
            create_certificate(network.org.ca_name, common_name)
            path = create_pkcs12(common_name)
            #Creating new certificate object
            certificate = Certificate()
            certificate.common_name = common_name
            certificate.ca_name = network.org.ca_name
            certificate.timestamp = datetime.now()
            certificate.user = client
            certificate.network = network
            certificate.save()
            request.session["path"] = path
            request.session["cert_id"] = certificate.id
    return HttpResponseRedirect('/openvpn/openvpn/main/')

@login_required
def download(request):
    try:
        path = request.session["path"]
        cert_id = request.session["cert_id"]
        certificate = Certificate.objects.get(id=cert_id)
        if certificate.downloaded:
            raise Exception()
    except:
        return HttpResponseRedirect('/openvpn/openvpn/main/')
    del request.session["path"]
    del request.session["cert_id"]
    response = HttpResponse(mimetype='application/zip')
    response['Content-Disposition'] = 'filename=openvpn-certificates.zip'
    buffer=StringIO()
    zip = zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED)
    zip.write(path)
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

	try:
            cert_id_p = request.POST['cert_id']

	    cert_id_s = None

	    try:
		cert_id_s = request.session['cert_id']
	    except:
		pass

	    if not cert_id_s is None and cert_id_p != cert_id_s:
                return HttpResponseRedirect('/openvpn/openvpn/main/')

            client = request.session["client"]
        except:
	    return HttpResponseRedirect('/openvpn/openvpn/main/')

	cert_id = cert_id_p
	certificate = None
        try:
            certificate = Certificate.objects.get(id = cert_id)

	    if certificate.revokated:
		return HttpResponseRedirect('/openvpn/openvpn/main/')
        except:
            pass
        certificates = client.certificate_set.all()
        
        if certificate in certificates:
            revoke_certificate(certificate.ca_name, certificate.common_name)
            certificate.revoked = True
            certificate.timestamp = datetime.now()
	    certificate.downloaded = True
            certificate.save()

            try:
                del request.session["path"]
                del request.session["cert_id"]
            except:
                pass
    return HttpResponseRedirect('/openvpn/openvpn/main/')

def logout_page(request):
    try:
        del request.session["client"]
        del request.session["organisations"]
        del request.session["cert_id"]
        del request.session["path"]
    except:
        pass
    
    logout(request)
    return HttpResponseRedirect('/openvpn/openvpn/')
