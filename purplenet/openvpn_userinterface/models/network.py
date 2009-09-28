# encoding: utf-8
# vim: shiftwidth=4 expandtab
#
# PurpleNet - a Web User Interface for OpenVPN
# Copyright (C) 2009  Santtu Pajukanta
# Copyright (C) 2008, 2009  Tuure Vartiainen, Antti Niemelä, Vesa Salo
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
The network and network profile models, other related models and
related exception classes.
"""

from django.db import models
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string

from libpurplenet.helpers import sanitize_name

class ConfigurationError(Exception):
    pass

class CircularInheritance(ConfigurationError):
    """CircularInheritance(Exception)
    
    This exception is raised by NetworkProfile.attributes if a circular
    inheritance is detected.
    """
    pass

class MixedModes(ConfigurationError):
    pass

class MixedProtocols(ConfigurationError):
    pass

class NoServers(ConfigurationError):
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
        """@property local_attributes(self) -> dict
        
        Returns a dictionary of attributes specified locally in this network
        profile. This does not include attributes inherited from other
        profiles.
        """
        for attribute in self.attribute_set.all():
            yield attribute.type.name, attribute.value

    @property
    def attributes(self):
        """@property attributes(self) -> dict
        
        Returns a dictionary of attributes specified either in inherited
        profiles or locally in this profile. The attributes specified locally
        are given greatest priority and thus override any attributes with the
        same name specified in inherited profiles. The priority between
        inherited profiles defining attributes with the same name is decided
        by the priority attribute of the inheritance relationship
        (ProfileInheritance object). In the event of equal priorities,
        it is up to the database which profile gets returned last and thus
        has its attributes remain.
        """
        data = {}
        self._flatten(data)
        return data

    def set_attribute(self, attr_type, value):
        """set_attribute(self, attr_type, value) -> NetworkAttribute
        
        Locally sets an attribute in this profile. The attribute type may be
        specified either by an attribute type object or the name of an
        attribute type.
        
        On a successful invocation a NetworkAttribute object is either updated
        or created. This object is returned.
        """
        if isinstance(attr_type, str):
            attr_type = NetworkAttributeType.objects.get(name=attr_type)

        try:
            # Existing attributes
            attr = self.attribute_set.get(
                profile=self,
                type=attr_type
            )
            attr.value = value
            attr.save()
        except NetworkAttribute.DoesNotExist:
            # New attributes
            attr = self.attribute_set.create(
                profile=self,
                type=attr_type,
                value=value
            )
        
        return attr
    
    def clear_attribute(self, attr_type):
        """clear_attribute(self, attr_type) -> bool
        
        Removes a local attribute. The attribute type may be specified by
        either an attribute type object or the name of an attribute type.
        
        The return value indicates whether an attribute was found and removed
        or not.
        """
        if isinstance(attr_type, str):
            attr_type = NetworkAttributeType.objects.get(name=attr_type)
        
        try:
            attr = self.attribute_set.get(
                profile=self,
                type=attr_type
            )
            attr.delete()
            return True
        except NetworkAttribute.DoesNotExist:
            return False
    
    def inherit(self, profile, priority=0):
        """inherit(self, profile, priority=0)
        
        Makes this NetworkProfile inherit another NetworkProfile. The profile
        to be inherited may be specified by a NetworkProfile object, its
        primary key (an integer) or the name of the profile (a string).
        
        An optional integer parameter, priority, may be specified, which will
        be used to specify in which multiple profiles are inherited. A lower
        priority number specifies a higher priority.
        """
        if isinstance(profile, str):
            profile = NetworkProfile.objects.get(name=profile)
        
        ProfileInheritance(
            inheritor=self,
            target=profile,
            priority=priority
        ).save()

    def _flatten(self, data, stack_contents=set()):
        """_flatten(self, data, stack_contents=set())
        
        The recursive implementation of the "attributes" property. Do not
        call directly. 
        """
        # Don't blow the stack even if there's a loop in the inheritance
        # diagram.
        if self in stack_contents:
            raise CircularInheritance
        
        stack_contents.add(self)
        
        # Descending sort to get the most important last so more important
        # profiles override those less important.
        heritage = ProfileInheritance.objects.filter(
            inheritor=self).order_by("-priority")
        
        # Depth first        
        for heirloom in heritage:
            # Get the attributes from each of the inherited profiles
            heirloom.target._flatten(data)

        # Finally, get local attributes
        data.update(self.local_attributes)

        # Avoid false positives on the classical Diamond Problem of multiple
        # inheritance
        stack_contents.remove(self)

    def may_be_managed_by(self, client):
        return client.is_superuser
    
    @property
    def manage_url(self):
        return reverse("manage_network_page", kwargs={"network_id":self.id})

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
        ordering = ("inheritor", "-priority",)

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
    #owner = models.ForeignKey("Org", related_name="owned_network_set")
    server_set = models.ManyToManyField("Server", blank=True, null=True)
    profile = models.ForeignKey(NetworkProfile, related_name="user_set")
    #server_ca = models.ForeignKey("ServerCA")

    # REVERSE: orgs_that_have_access_set = ManyToMany(Org)
    
    def __unicode__(self):
        return self.name

    def may_be_managed_by(self, client):
        return client.is_superuser
    
    @property
    def manage_url(self):
        return reverse("manage_network_page", kwargs={"network_id":self.id})

    @property
    def sanitized_name(self):
        return sanitize_name(self.name)

    @property
    def _config_vars(self):
        servers = self.server_set.all()
        if not servers:
            raise NoServers()
    
        some_server = servers[0]
        mode = some_server.mode
        protocol = some_server.protocol
        
        if not all(server.mode == mode for server in servers):
            raise MixedModes()
        
        if not all(server.protocol == protocol for server in servers):
            raise MixedProtocols()
        
        vars = dict(
            tun_tap="tun" if mode == "routed" else "tap",
            protocol=protocol,
            servers=servers
        )
        
        return vars

    def client_config(self, keys_filename="keys.p12"):
        return render_to_string("openvpn_conf/client.conf",
            dict(self._config_vars, keys_filename=keys_filename))

    class Admin: pass

    class Meta:
        app_label = "openvpn_userinterface"

