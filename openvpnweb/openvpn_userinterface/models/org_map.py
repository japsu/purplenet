# encoding: utf-8
# vim: shiftwidth=4 expandtab

from django.db import models
from django.contrib.auth.models import Group

class MappingType(models.Model):
    name = models.CharField(max_length=60)
    description = models.CharField(max_length=400)
    source_name = models.CharField(max_length=200)
    
    NAMESPACE_CHOICES = [
        ("env", "Environment variables")
    ]
    namespace = models.CharField(max_length=30, choices=NAMESPACE_CHOICES,
        default="env")

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = "openvpn_userinterface"

class OrgMapping(models.Model):
    group = models.ForeignKey(Group)
    # REVERSE: element_set = ForeignKey(MappingElement)

    def __unicode__(self):
        return u"%s %s" % (
            self.group.name,
    
            u", ".join(u'%s:%s="%s"' % (
                elem.type.namespace,
                elem.type.source_name,
                elem.value
            ) for elem in self.element_set.all())
        )

    class Meta:
        app_label = "openvpn_userinterface"

class MappingElement(models.Model):
    type = models.ForeignKey(MappingType, related_name="element_set")
    mapping = models.ForeignKey(OrgMapping, related_name="element_set")
    value = models.CharField(max_length=200)

    def matches(self, client):
        if self.type.namespace != "env":
            raise AssertionError("The only implemented namespace is 'env'")
        
        value_from_env = os.environ.get(self.type.source_name, None)
        return self.value == value_from_env

    class Meta:
        app_label = "openvpn_userinterface"

