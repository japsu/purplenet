# encoding: utf-8
# vim: shiftwidth=4 expandtab

from django import forms
from django.contrib.formtools.wizard import FormWizard

from openvpnweb.openvpn_userinterface.models import *

class CAForm(forms.Form):
    root_ca_cn = forms.CharField(max_length=30, initial="Root CA")
    root_ca_dir = forms.CharField(max_length=200)

    server_ca_cn = forms.CharField(max_length=30, initial="Server CA")
    server_ca_dir = forms.CharField(max_length=200)

    client_ca_cn = forms.CharField(max_length=30, initial="Client CA")
    client_ca_dir = forms.CharField(max_length=200)

class OrgForm(forms.Form):
    org_name = forms.CharField(max_length=80)
    cn_suffix = forms.CharField(max_length=30)
    ca_dir = forms.CharField(max_length=200)

class OrgMapForm(forms.Form):
    pass

class ServerForm(forms.ModelForm):
    class Meta:
        model = Server
        fields = [
            "name",
            "address",
            "port",
            "protocol",
            "mode"
        ]

class NetworkForm(forms.Form):
    network_name = forms.CharField(max_length=30)
