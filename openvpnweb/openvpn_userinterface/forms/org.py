# encoding: utf-8
# vim: shiftwidth=4 expandtab

from django import forms

class CreateOrgForm(forms.Form):
    name = forms.CharField(max_length=80, label="Name")
    cn_suffix = forms.CharField(max_length=30, label="CN suffix")