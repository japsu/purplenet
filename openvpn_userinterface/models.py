from django.db import models

class Org(models.Model):
        name = models.CharField(max_length=30)
	ca_name = models.CharField(max_length=30)
	cn_suffix = models.CharField(max_length=30)        

        def __str__(self):
            return self.name
        def __repr__(self):
            return self.name
        
        class Admin: pass

class Client(models.Model):
    name = models.CharField(max_length=30)
    orgs = models.ManyToManyField(Org, null=True)
    def __str__(self):
        return self.name
    
    def __repr__(self):
        return self.name
    
    class Admin: pass
                            
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
    
    def __str__(self):
        return self.name
        
    def __repr__(self):
        return self.name
                
    class Admin: pass

class Network(models.Model):
    name = models.CharField(max_length=30)
    org = models.ForeignKey(Org)
    server = models.ForeignKey(Server)
    
    def __str__(self):
        return self.name
   
    def __repr__(self):
        return self.name
    
    class Admin: pass
    
class Network_attribute(models.Model):
    name = models.CharField(max_length=30)
    value = models.CharField(max_length=30)
    networks = models.ManyToManyField(Network)
    
    def __str__(self):
        return self.name
    
    class Admin: pass
        
class Certificate(models.Model):
    common_name = models.CharField(max_length=30)
    ca_name = models.CharField(max_length=30)
    timestamp = models.DateTimeField()
    revoked = models.BooleanField(default=False)
    user = models.ForeignKey(Client)
    network = models.ForeignKey(Network)
    downloaded = models.BooleanField(default=False)
    
    def __str__(self):
        return self.common_name
    def __repr__(self):
        return self.common_name
    
    class Admin:
        list_display = ('revoked','downloaded','common_name','user','network','timestamp')
        list_filter = ['network','revoked','user']
        search_fields = ['user','network','common_name']
