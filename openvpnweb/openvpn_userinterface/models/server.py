# encoding: utf-8
# vim: shiftwidth=4 expandtab

from django.db import models

class Server(models.Model):
    name = models.CharField(max_length=30)
    address = models.IPAddressField()
    port = models.IntegerField(max_length=10)
    PROTOCOL_CHOICES = (
        ('tcp','TCP'),
        ('udp','UDP')
    )
    MODE_CHOICES = (
        ('bridged','BRIDGED'),
        ('routed','ROUTED')
    )
    protocol = models.CharField(max_length=30, choices=PROTOCOL_CHOICES)
    mode = models.CharField(max_length=30, choices=MODE_CHOICES) 
    certificate = models.OneToOneField("ServerCertificate",
        related_name="user")

    # REVERSE: network_set = ManyToMany(Network)
    
    def __unicode__(self):
        return self.name

    class Admin: pass

    class Meta:
        app_label = "openvpn_userinterface"

