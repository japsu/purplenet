# encoding: utf-8
# vim: shiftwidth=4 expandtab

from django.db import models
from django.contrib.auth.models import User, Group
from openvpnweb.openvpn_userinterface.models.org import Org
from openvpnweb.openvpn_userinterface.models.siteconfig import SiteConfig

class Client(models.Model):
    user = models.OneToOneField(User)

    @property
    def name(self):
        return self.user.username

    @property
    def orgs(self):
        return Org.objects.filter(group__in=self.user.groups.all())

    @property
    def managed_org_set(self):
        if self.is_superuser:
            return Org.objects.all()
        else:
            return Org.objects.filter(
                admin_group_set__group__in=self.user.groups.all())
        
    @property
    def is_superuser(self):
        superuser_group = SiteConfig.objects.get().superuser_group
        return superuser_group in self.user.groups.all()

    def __unicode__(self):
        return self.name

    def may_access(self, org, net):
        return org in self.orgs and org.may_access(net)

    def may_revoke(self, certificate):
        return certificate.owner == self or \
            self.may_manage(certificate.ca.org)

    def may_manage(self, org_or_group):
        if isinstance(org_or_group, Group):
            group = org_or_group
            
            try:
                # user group
                org = Org.objects.get(group=group)
                return self.may_manage(org)
            except:
                # admin or other group
                return self.is_superuser()
        else:
            if self.is_superuser:
                return True
            
            # assume Org
            org = org_or_group
            
            groups = set(ag.group for ag in org.admin_group_set.all())
            return bool(groups.intersection(self.user.groups.all()))
            
            
    def may_view_management_pages(self):
        return self.is_superuser or bool(self.managed_org_set)

    class Admin: pass

    class Meta:
        app_label = "openvpn_userinterface"

