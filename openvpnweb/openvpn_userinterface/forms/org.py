# encoding: utf-8
# vim: shiftwidth=4 expandtab

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
        