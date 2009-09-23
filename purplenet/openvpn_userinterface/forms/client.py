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
Forms related to the Client model.
"""

from django import forms
from django.forms.util import ErrorList

from django.contrib.auth.models import User

class PasswordField(forms.CharField):
    widget = forms.PasswordInput

class ClientForm(forms.Form):
    username = forms.CharField(max_length=30, label="Username")
    first_name = forms.CharField(max_length=30, required=False,
        label="First name")
    last_name = forms.CharField(max_length=30, required=False,
        label="Last name")

class CreateClientForm(ClientForm):
    password = PasswordField(max_length=2048, label="Password",
        required=False)
    password_again = PasswordField(max_length=2048, label="Password (again)",
        required=False)
    
    def clean(self):
        cleaned_data = self.cleaned_data
        
        password = cleaned_data.get("password")
        password_again = cleaned_data.get("password_again")
        
        if password and password != password_again:
            msg = "The passwords do not match."
            self._errors["password"] = ErrorList([msg])
            self._errors["password_again"] = ErrorList([msg])
            
            del cleaned_data["password"]
            del cleaned_data["password_again"]
            
        return cleaned_data

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "first_name", "last_name"]