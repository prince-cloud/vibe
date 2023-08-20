from django.contrib import admin
from .models import Group, Community, Announcement
# Register your models here.


admin.site.register(Group)
admin.site.register(Community)
admin.site.register(Announcement)