# encoding: utf-8
# vim: shiftwidth=4 expandtab

from django import forms
from django.contrib.auth.models import Group

from ..models import Network, Server, NetworkProfile

class SelectGroupForm(forms.Form):
    group = forms.ModelChoiceField(queryset=Group.objects.all(), label="Group")
    
class SelectNetworkForm(forms.Form):
    network = forms.ModelChoiceField(queryset=Network.objects.all(), label="Network")

class SelectServerForm(forms.Form):
    server = forms.ModelChoiceField(queryset=Server.objects.all(), label="Server")

class SelectProfileForm(forms.Form):
    profile = forms.ModelChoiceField(queryset=NetworkProfile.objects.all(), label="Profile")