# encoding: utf-8
# vim: shiftwidth=4 expandtab

from django.db import models
from django.contrib.auth.models import User
from openvpnweb.openvpn_userinterface.models.org import Org

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
        return Org.objects.filter(
            admin_group_set__in=self.user.groups.all())
        
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

    def may_manage(self, org):
        return self.is_superuser or bool(set(org.admin_group_set.all())
            .intersection(self.user.groups.all()))

    def may_view_management_pages(self):
        return bool(self.managed_org_set)

    class Admin: pass

    class Meta:
        app_label = "openvpn_userinterface"

