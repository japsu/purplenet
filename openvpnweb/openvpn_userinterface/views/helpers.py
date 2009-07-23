from django.shortcuts import render_to_response
from django.template import RequestContext

def post_confirmation_page(request, question, choices):
    """post_confirmation_page(request, question, choices) -> response

    A helper for implementing the lo-REST protocol. Should a POST-only resource
    be accessed with the GET method, this method may be used to return a
    confirmation page that allows the user to retry with the POST method or
    cancel.
    """

    client = request.session.get("client", None)

    vars = RequestContext(request, {
        "question" : question,
        "choices" : choices,
        "client" : client,
    })
    return render_to_response("openvpn_userinterface/confirmation.html", vars)

