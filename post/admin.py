from django.contrib import admin
# Register your models here.
from .models import (
    Post,
    PostComment,
    PostPicture, 
    PostVideo, 
)


# @admin.register(Post)
# class PostAdmin(Model):
#     class PostResources():
#         class Meta:
#             model = Post
#     list_display = [
#         "text",
#         "user",
#         "post_type",
#         "shared_from",
#         "is_edited",
#         "date_created",
#     ]
#     list_filter = [
#         "is_edited",
#         "post_type",
#     ]
#     search_fields = [
#         "user",
#         "text",
#     ]

admin.site.register(Post)
admin.site.register(PostPicture)
admin.site.register(PostComment) 
admin.site.register(PostVideo) 
