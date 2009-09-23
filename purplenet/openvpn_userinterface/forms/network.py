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
Forms related to the Network and NetworkProfile models.
"""

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

# TODO Make ExtendedProfileForm grab its fields from NetworkAttributeType.objects.all()
class ExtendedProfileForm(forms.Form):
    name = forms.CharField(max_length=30, label="Name")
    vlan = forms.CharField(max_length=6, label="VLAN number", required=False)
    network_id = forms.CharField(max_length=15, label="Network address", required=False)
    netmask = forms.CharField(max_length=15, label="Netmask", required=False)
    gateway = forms.CharField(max_length=15, label="Gateway", required=False)
    dns = forms.CharField(max_length=200, label="DNS", required=False)
    route = forms.CharField(max_length=200, label="Routes", required=False)