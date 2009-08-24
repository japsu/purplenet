# encoding: utf-8
# vim: shiftwidth=4 expandtab

from django import forms
from django.contrib.auth.models import Group

from openvpnweb.openvpn_userinterface.models import Network, Server

class SelectGroupForm(forms.Form):
    group = forms.ModelChoiceField(queryset=Group.objects.all(), label="Group")
    
class SelectNetworkForm(forms.Form):
    network = forms.ModelChoiceField(queryset=Network.objects.all(), label="Network")

class SelectServerForm(forms.Form):
    server = forms.ModelChoiceField(queryset=Server.objects.all(), label="Server")