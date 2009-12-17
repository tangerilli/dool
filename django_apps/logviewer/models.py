from django.db import models

class Account(models.Model):
    protocol = models.CharField(max_length=255)
    uid = models.CharField(max_length=255)
    full_name = models.CharField(max_length=255, default="")
    owned = models.BooleanField(default=False)
    
    def __unicode__(self):
        return self.protocol + u' - ' + self.uid
        
class Message(models.Model):
    timestamp = models.DateTimeField()
    text = models.TextField()
    sender = models.ForeignKey(Account, related_name='sender_messages')
    receiver = models.ForeignKey(Account, related_name='receiver_messages')
    host = models.CharField(max_length=255)
    client_type = models.CharField(max_length=255)
    
    def sent(self):
        return self.sender.owned
        
    def received(self):
        return not self.sent()
        
    def __unicode__(self):
        return unicode(self.sender) + u' - ' + unicode(self.timestamp)