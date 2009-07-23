# encoding: utf-8
# vim: shiftwidth=4 expandtab

from django import forms
from django.contrib.formtools.wizard import FormWizard

class CAForm(forms.Form):
    root_ca_cn = forms.CharField(max_length=30, initial="Root CA")
    server_ca_cn = forms.CharField(max_length=30, initial="Server CA")
    client_ca_cn = forms.CharField(max_length=30, initial="Client CA")

class OrgForm(forms.Form):
    org_name = forms.CharField(max_length=80)

class OrgMapForm(forms.Form):
    pass

class ServerForm(forms.Form):
    pass

class NetworkForm(forms.Form):
    pass

SETUP_WIZARD_FORM_LIST = [
    CAForm,
    OrgForm,
    OrgMapForm,
    ServerForm,
    NetworkForm
]

class SetupWizard(FormWizard):
    def done(self, request, form_list):
        pass

    def get_template(self, step):
        return "openvpn_userinterface/setupwizard.html"
