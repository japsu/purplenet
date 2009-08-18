# encoding: utf-8
# vim: shiftwidth=4 expandtab

from django.db import models
from django.contrib.auth.models import Group
from openvpnweb.helper_functions import generate_random_string 

class Org(models.Model):
    group = models.OneToOneField(Group, related_name="org")
    cn_suffix = models.CharField(max_length=30)    
        
    admin_group_set = models.ManyToManyField(Group, null=True, blank=True,
        related_name="managed_org_set")
    client_ca = models.ForeignKey("ClientCA", null=True, blank=True,
        related_name="user_set")    
    accessible_network_set = models.ManyToManyField("Network", null=True,
        blank=True, related_name="orgs_that_have_access_set")

    # REVERSE: owned_network_set = ForeignKey(Network)

    @property
    def name(self):
        return self.group.name

    @property
    def ca_name(self):
        return self.ca.common_name

    def __unicode__(self):
        return self.name

    def get_random_cn(self):
        return generate_random_string() + self.cn_suffix

    def may_access(self, network):
        return network in self.accessible_network_set.all()
    
    class Admin: pass

    class Meta:
        app_label = "openvpn_userinterface"

