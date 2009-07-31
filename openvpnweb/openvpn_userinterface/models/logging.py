# encoding: utf-8
# vim: shiftwidth=4 expandtab

from django.db import models
from django.contrib.auth.models import Group

class LogEntry(models.Model):
    timestamp = models.DateTimeField(auto_now=True)

    EVENT_CHOICES = [
        ("client.new", "New client registered"),
        ("org_map.client_added_to_group", "User mapped into a group"),
        ("org_map.client_removed_from_group", "User de-mapped from a group"),
        ("client_certificate.create", "Client certificate created"),
        ("client_certificate.revoke", "Client certificate revoked"),
    ]
    event = models.CharField(max_length=30, choices=EVENT_CHOICES)

    denied = models.BooleanField(default=False)
    client = models.ForeignKey("Client")
    client_certificate = models.ForeignKey("ClientCertificate", null=True,
        blank=True, related_name="log_entry_set")
    group = models.ForeignKey(Group, null=True, blank=True,
        related_name="log_entry_set")
    network = models.ForeignKey("Network", null=True, blank=True,
        related_name="log_entry_set")

    class Meta:
        app_label = "openvpn_userinterface"
