# encoding: utf-8
# vim: shiftwidth=4 expandtab

from django import forms

from ..models import Network, NetworkProfile

class NetworkForm(forms.ModelForm):
    class Meta:
        model = Network
        fields = ["name"]

class ProfileForm(forms.ModelForm):
    class Meta:
        model = NetworkProfile
        fields = ["name"]

# FIXME Make ExtendedProfileForm grab its fields from NetworkAttributeType.objects.all()
class ExtendedProfileForm(forms.Form):
    name = forms.CharField(max_length=30, label="Name")
    vlan = forms.CharField(max_length=6, label="VLAN number", required=False)
    network_id = forms.CharField(max_length=15, label="Network address", required=False)
    netmask = forms.CharField(max_length=15, label="Netmask", required=False)
    gateway = forms.CharField(max_length=15, label="Gateway", required=False)
    dns = forms.CharField(max_length=200, label="DNS", required=False)
    route = forms.CharField(max_length=200, label="Routes", required=False)