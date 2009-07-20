#!/usr/bin/env python
# encoding: utf-8
# vim: shiftwidth=4 expandtab

from openvpnweb.openvpn_userinterface.models import *
from django.contrib.auth.models import Group

def setup_org_map():
    dept_number_type = MappingType(
        name="Department number (Shibboleth ENV)",
        description="Matches the 5-digit department number from the " +
            "Shibboleth single sign-on service.",
        source_name="departmentNumber",
        namespace="env"
    )
    dept_number_type.save()

    dce_group = Group(name="TUT Department of Communications Engineering")
    dce_group.save()

    dce_admin_group = Group(name="TUT Department of Communications Engineering (Administrators)")
    dce_admin_group.save()

    dce_org = Org(
        group=dce_group,
        cn_suffix=".rd.tut.fi"
    )
    dce_org.save()

    dce_org.admin_group_set.add(dce_admin_group)
    dce_org.save()

    for dept_number in xrange(90601, 90606):
        dept_number_to_dce_mapping = OrgMapping(group=dce_group)
        dept_number_to_dce_mapping.save()
        dept_number_to_dce_mapping.element_set.create(
            type=dept_number_type,
            value=str(dept_number)
        )

def main():
    from sys import environ
    environ["DJANGO_CONFIG_MODULE"] = "openvpnweb.settings"

    setup_org_map()

if __name__ == "__main__":
     main()
