from django.db import models
from accounts.models import CustomUser
# Create your models here.

class Group(models.Model):
    name = models.CharField(max_length=100)
    admin = models.ForeignKey(CustomUser, related_name="admin_groups", on_delete=models.CASCADE)
    members = models.ManyToManyField(CustomUser, related_name="group",)
    profile_picture = models.ImageField(upload_to='groups_profile/', null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return str(self.name)
    
    class Meta:
        ordering = ("-date_created",)
class Community(models.Model):
    name = models.CharField(max_length=100)
    admin = models.ForeignKey(CustomUser, related_name="admin_communities", on_delete=models.CASCADE)
    groups = models.ManyToManyField(Group, related_name="communities")
    profile_picture = models.ImageField(upload_to='communitu_profile/', null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return str(self.name)

    class Meta:
        ordering = ("-date_created",)   

class Announcement(models.Model):
    name = models.CharField(max_length=100)
    community = models.OneToOneField(Community, related_name="announcement", on_delete=models.CASCADE)

    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return str(self.community)
