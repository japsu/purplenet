# encoding: utf-8
# vim: shiftwidth=4 expandtab

from django import forms
from django.conf import settings
from tempfile import NamedTemporaryFile
from openvpnweb.openvpn_userinterface.models import *

import os

class WritableDirectoryField(forms.CharField):
    """
    Check that the field contains the name of a directory that is writable.
    """
    def clean(self, value):
        value = super(WritableDirectoryField, self).clean(value)

        if not value:
            raise forms.ValidationError('Enter a valid directory.')

        abspath = os.path.abspath(value)

        if not os.path.isdir(abspath):
            raise forms.ValidationError('Inaccessible or not a directory.')

        try:
            with NamedTemporaryFile(dir=abspath) as f:
                # Oh yeah, I believe you now. We can write here.
                pass
        except IOError:
            raise forms.ValidationError('Directory is not writable by the web server.')

        return abspath

class SetupKeyField(forms.CharField):
    widget = forms.PasswordInput

    def clean(self, value):
        value = super(SetupKeyField, self).clean(value)

        if settings.OPENVPNWEB_SETUP_KEY is None:
            raise forms.ValidationError("Setup is disabled from config")

        if not value == settings.OPENVPNWEB_SETUP_KEY:
            raise forms.ValidationError("The setup key does not match")

        return value

class SetupForm(forms.Form):
    setup_key = SetupKeyField(max_length=200,
        label="OPENVPNWEB_SETUP_KEY from settings.py")

    ca_dir = WritableDirectoryField(max_length=200, initial="/var/lib/openvpnweb/ca",
        label="Base directory for Certificate Authorities")

    root_ca_cn = forms.CharField(max_length=30, initial="Root CA",
        label="Common Name for the root CA")

    server_ca_cn = forms.CharField(max_length=30, initial="Server CA",
        label="Common Name for the server CA")

    client_ca_cn = forms.CharField(max_length=30, initial="Client CA",
        label="Common Name for the client CA")
