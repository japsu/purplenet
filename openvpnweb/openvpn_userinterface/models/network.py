# encoding: utf-8
# vim: shiftwidth=4 expandtab

from django.db import models

class NetworkProfile(models.Model):
    name = models.CharField(max_length=30)
    inherited_profile_set = models.ManyToManyField('self', null=True,
        blank=True, symmetrical=False, related_name="inheritor_set")
    # REVERSE: inherited_by = ManyToMany(self)

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = "openvpn_userinterface"

class NetworkAttributeType(models.Model):
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=2000)
    regex = models.CharField(max_length=200)
    multiple = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = "openvpn_userinterface"

class NetworkAttribute(models.Model):
    profile = models.ForeignKey(NetworkProfile)
    type = models.ForeignKey(NetworkAttributeType)
    value = models.CharField(max_length=200)

    def __unicode__(self):
        return "%s = %s" % (self.type, self.value)

    class Meta:
        app_label = "openvpn_userinterface"

class Network(models.Model):
    name = models.CharField(max_length=30)
    owner = models.ForeignKey("Org", related_name="owned_network_set")
    server_set = models.ManyToManyField("Server")
    profile_set = models.ManyToManyField(NetworkProfile, blank=True,
        null=True, related_name="user_set")
    server_ca = models.ForeignKey("ServerCA")

    # REVERSE: orgs_that_have_access_set = ManyToMany(Org)
    
    def __unicode__(self):
        return self.name

    class Admin: pass

    class Meta:
        app_label = "openvpn_userinterface"

