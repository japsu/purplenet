from django.db import models
from django.contrib.auth.models import Group

class SiteConfig(models.Model):
    superuser_group = models.OneToOneField(Group)
    
    root_ca = models.OneToOneField("IntermediateCA", related_name="int_scfg_rca")
    server_ca = models.OneToOneField("ServerCA", related_name="int_scfg_sca")
    client_ca = models.OneToOneField("IntermediateCA", related_name="int_scfg_cca")
    
    class Meta:
        app_label = "openvpn_userinterface"
        
class InterestingEnvVar(models.Model):
    name = models.CharField(max_length=200)
    
    class Meta:
        app_label = "openvpn_userinterface"