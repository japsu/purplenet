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
Search forms that take a textual search term and return single or multiple
search results by performing model queries.
"""

from django import forms
from django.forms.util import ErrorList
from django.contrib.auth.models import Group

from ..models import Client

class SearchForm(forms.Form):
    _model_field = "name"
    _search_method = "exact"
    _allow_multiple_results = False
    _search_result = None
    
    @property
    def search_result(self):
        return self._search_result
        
    def _perform_search(self):
        kwargs = {
            "%s__%s" % (self._model_field, self._search_method) :
                self.cleaned_data["search_field"]
        }
        
        if self._allow_multiple_results:
            self._search_result = self._model.objects.filter(**kwargs)
        else:
            self._search_result = self._model.objects.get(**kwargs)
    
    def clean(self):
        cleaned_data = self.cleaned_data
        
        if "search_field" in cleaned_data:
            msg = None
            
            try:
                self._perform_search()
            except self._model.DoesNotExist:
                msg = "%s not found." % (self._model._meta.verbose_name)
            except self._model.MultipleObjectsReturned:
                msg = "Multiple %s found." % (self._model._meta.verbose_name_plural)

            if msg is not None:
                self._errors["search_field"] = ErrorList([msg])
                del cleaned_data["search_field"]
        
        return cleaned_data
    
class ClientSearchForm(SearchForm):
    _model = Client
    _model_field = "user__username"

    search_field = forms.CharField(max_length=30, label="Username")

class GroupSearchForm(SearchForm):
    _model = Group
    
    search_field = forms.CharField(max_length=30, label="Group name")

        