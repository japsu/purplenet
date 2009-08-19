from django import forms
from django.forms.util import ErrorList

class PasswordField(forms.CharField):
    widget = forms.PasswordInput

class CreateClientForm(forms.Form):
    username = forms.CharField(max_length=30, label="Username")
    first_name = forms.CharField(max_length=30, required=False,
        label="First name")
    last_name = forms.CharField(max_length=30, required=False,
        label="Last name")
    
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