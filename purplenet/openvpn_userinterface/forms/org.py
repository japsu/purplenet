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
Forms related to the Org model.
"""

from django import forms
from ..models import dump_org_map, validate_org_map

class CreateOrgForm(forms.Form):
    name = forms.CharField(max_length=80, label="Name")
    cn_suffix = forms.CharField(max_length=30, label="CN suffix")
    
class OrgMapForm(forms.Form):
    org_map = forms.CharField(max_length=32768, widget=forms.widgets.Textarea,
        label="Organizational mapping", initial=lambda: dump_org_map())
    
    def clean(self):
        cleaned_data = self.cleaned_data
        
        org_map = cleaned_data.get("org_map")
        
        if org_map:
            try:
                validate_org_map(org_map)
            except OrgMapSyntaxError, e:
                msg = "Syntax error: " + str(e)
                self._errors["org_map"] = ErrorList([msg])
                del cleaned_data["org_map"]
            
        return cleaned_data    
        