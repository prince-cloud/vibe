from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

app_name = "Post"

router = DefaultRouter()

router.register("posts", views.PostViewSet, basename="posts")
router.register("posts-pics", views.PostPictureViewSet, basename="post-pics")
router.register("post-comments", views.PostCommentViewSet, basename="posts-comments")
router.register("post-video", views.PostVideoViewset, basename="post-video")

urlpatterns = [
    path("", include(router.urls)),
]
