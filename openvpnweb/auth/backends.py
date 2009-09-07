from django.contrib.auth.models import User
from os import environ

class ShibbolethBackend:
    def authenticate(self):
        username = environ.get("uid")
        if not username:
            return None
        
        user, created = User.objects.get_or_create(
            username=username,
            defaults=dict(
               first_name=environ.get("givenName"),
               last_name=environ.get("sn")   
            )
        )
        return user