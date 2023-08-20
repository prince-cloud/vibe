from django.db import models
from accounts.models import CustomUser
# Create your models here.

class Group(models.Model):
    name = models.CharField(max_length=100)
    admin = models.ForeignKey(CustomUser, related_name="admin_groups", on_delete=models.CASCADE)
    members = models.ManyToManyField(CustomUser, related_name="group",)
    
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return str(self.name)
    
class Community(models.Model):
    name = models.CharField(max_length=100)
    admin = models.ForeignKey(CustomUser, related_name="admin_communities", on_delete=models.CASCADE)
    groups = models.ManyToManyField( Group, related_name="communities")

    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return str(self.name)

class Announcement(models.Model):
    name = models.CharField(max_length=100)
    coummunity = models.OneToOneField(Community, related_name="announcement", on_delete=models.CASCADE)

    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return str(self.name)
