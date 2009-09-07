# encoding: utf-8
# vim: shiftwidth=4 expandtab

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required

from ..models import ClientCertificate
from ..logging import log

@login_required
def main_page(request):
    client = request.session["client"]
    
    # XXX try to replace with smarter queries
    data = client.get_certificates()

    variables = RequestContext(request, {
        'data': data,
        'client': client,
    })
    
    return render_to_response(
        'openvpn_userinterface/main_page.html', variables 
    )

