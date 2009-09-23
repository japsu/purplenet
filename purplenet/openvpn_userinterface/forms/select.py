# encoding: utf-8
# vim: shiftwidth=4 expandtab
#
# PurpleNet - a Web User Interface for OpenVPN
# Copyright (C) 2009  Santtu Pajukanta
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
Selection forms that present the user with a drop-down menu to select
objects from a model.
""" 

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