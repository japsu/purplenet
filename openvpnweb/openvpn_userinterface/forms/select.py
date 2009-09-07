# encoding: utf-8
# vim: shiftwidth=4 expandtab

from django import forms

from ..models import Network, Server, NetworkProfile, Org, AdminGroup

class SelectAdminGroupForm(forms.Form):
    group = forms.ModelChoiceField(queryset=AdminGroup.objects.all(), label="Admin group")
    
class SelectNetworkForm(forms.Form):
    network = forms.ModelChoiceField(queryset=Network.objects.all(), label="Network")

class SelectServerForm(forms.Form):
    server = forms.ModelChoiceField(queryset=Server.objects.all(), label="Server")

class SelectProfileForm(forms.Form):
    profile = forms.ModelChoiceField(queryset=NetworkProfile.objects.all(), label="Profile")
    
class SelectOrgForm(forms.Form):
    org = forms.ModelChoiceField(queryset=Org.objects.all(), label="Organization")