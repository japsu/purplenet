# encoding: utf-8
# vim: shiftwidth=4 expandtab

from django import forms

class SimpleNetworkForm(forms.Form):
    name = forms.CharField(max_length=30)
    vlan = forms.IntegerField(required=False)
    network_id = forms.CharField(max_length=15)
    netmask = forms.CharField(max_length=15)
    gateway = forms.CharField(max_length=15, required=False)
    dns = forms.CharField(max_length=15, required=False)
