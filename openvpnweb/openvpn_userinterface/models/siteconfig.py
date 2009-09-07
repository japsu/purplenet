from django.db import models
from django.contrib.auth.models import Group

import os

class SiteConfig(models.Model):
    superuser_group = models.OneToOneField(Group)
    
    root_ca = models.OneToOneField("IntermediateCA", related_name="int_scfg_rca", null=True, blank=True)
    server_ca = models.OneToOneField("ServerCA", related_name="int_scfg_sca", null=True, blank=True)
    client_ca = models.OneToOneField("IntermediateCA", related_name="int_scfg_cca", null=True, blank=True)
    
    ca_base_dir = models.CharField(max_length=200)
    
    @property
    def copies_dir(self):
        return os.path.join(self.ca_base_dir, "copies")
    
    class Meta:
        app_label = "openvpn_userinterface"
        
class InterestingEnvVar(models.Model):
    name = models.CharField(max_length=200)
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        app_label = "openvpn_userinterface"