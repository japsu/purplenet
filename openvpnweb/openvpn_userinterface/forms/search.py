# encoding: utf-8
# vim: shiftwidth=4 expandtab

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
        return _search_result
        
    def _perform_search(self):
        kwargs = {
            "%s__%s" % (self._model_field, self.s_earch_method) :
                self.cleaned_data["search_field"]
        }
        
        if allow_multiple_results:
            _search_result = self.model.objects.filter(**kwargs)
        else:
            _search_result = self.model.objects.get(**kwargs)
    
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

        