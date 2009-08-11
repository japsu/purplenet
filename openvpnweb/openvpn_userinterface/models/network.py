# encoding: utf-8
# vim: shiftwidth=4 expandtab

from django.db import models

class CircularInheritance(Exception):
    pass

class NetworkProfile(models.Model):
    name = models.CharField(max_length=30)
    inherited_profile_set = models.ManyToManyField('self', null=True,
        blank=True, symmetrical=False, related_name="inheriting_profile_set",
        through="ProfileInheritance")
    # REVERSE: inheriting_profile_set = ManyToMany(self)
    # REVERSE: attribute_set = ForeignKey(NetworkAttribute)

    @property
    def local_attributes(self):
        for attribute in self.attribute_set.all():
            yield attribute.type.name, attribute.value

    @property
    def attributes(self):
        data = {}
        self._flatten(data)
        return data

    def set_attribute(self, attr_type, value):
        if isinstance(attr_type, str):
            attr_type = NetworkAttributeType.objects.get(name=attr_type)

        try:
            attr = self.attribute_set.get(
                profile=self,
                type=attr_type
            )
            attr.value = value
            attr.save()
        except NetworkAttribute.DoesNotExist:
            attr = self.attribute_set.create(
                profile=self,
                type=attr_type,
                value=value
            )
    
    def inherit(self, profile, priority=0):
        if isinstance(profile, str):
            profile = NetworkProfile.objects.get(name=profile)
        elif isinstance(profile, int):
            profile = NetworkProfile.objects.get(pk=profile)
        
        ProfileInheritance(
            inheritor=self,
            target=profile,
            priority=priority
        ).save()

    def _flatten(self, data, stack_contents=set()):
        
        if self in stack_contents:
            raise CircularInheritance
        
        stack_contents.add(self)
        
        # Descending sort to get the most important last so more important
        # profiles override those less important.
        heritage = ProfileInheritance.objects.filter(
            inheritor=self).order_by("-priority")
        
        # Depth first        
        for heirloom in heritage:
            inherited_profile = heirloom.target
            inherited_profile._flatten(data)

        data.update(self.local_attributes)
        
        stack_contents.remove(self)

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = "openvpn_userinterface"

class ProfileInheritance(models.Model):
    inheritor = models.ForeignKey(NetworkProfile, related_name="int_inhr_set")
    target = models.ForeignKey(NetworkProfile, related_name="int_inee_set")

    priority = models.IntegerField(default=0)

    class Meta:
        app_label = "openvpn_userinterface"
        ordering = ("-priority",)

class NetworkAttributeType(models.Model):
    name = models.CharField(max_length=30, unique=True)
    description = models.CharField(max_length=200)
    regex = models.CharField(max_length=200)
    multiple = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = "openvpn_userinterface"

class NetworkAttribute(models.Model):
    profile = models.ForeignKey(NetworkProfile, related_name="attribute_set")
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

