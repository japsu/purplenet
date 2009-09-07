# encoding: utf-8
# vim: shiftwidth=4 expandtab

from django.db import models
from django.contrib.auth.models import Group
from django.core.urlresolvers import reverse
from openvpnweb.helper_functions import generate_random_string 

class Org(models.Model):
    group = models.OneToOneField(Group, related_name="org")
    cn_suffix = models.CharField(max_length=30)    
        
    admin_group_set = models.ManyToManyField("AdminGroup", null=True, blank=True,
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
        prefix = generate_random_string()
        suffix = self.cn_suffix
        
        if suffix.startswith("."):
            return prefix + suffix
        else:
            return prefix + "." + suffix

    def may_access(self, network):
        return network in self.accessible_network_set.all()
    
    def may_be_managed_by(self, client):
        # TODO: move access control logic here from client
        return client.may_manage(self)
    
    @property
    def manage_url(self):
        return reverse("manage_org_page", kwargs={"org_id":self.id})
    
    class Admin: pass

    class Meta:
        app_label = "openvpn_userinterface"

class AdminGroup(models.Model):
    group = models.OneToOneField(Group, related_name="int_agrp_ref", unique=True)
    
    @property
    def name(self):
        return self.group.name
    
    def __unicode__(self):
        return self.group.name
    
    def may_be_managed_by(self, client):
        return client.is_superuser or client.user in self.group.user_set.all()
    
    @property
    def manage_url(self):
        return reverse("manage_admin_group_page", kwargs={"admin_group_id":self.id})
    
    class Meta:
        app_label = "openvpn_userinterface"