from django.db import models
from accounts.models import CustomUser 
from django.contrib.auth import get_user_model
# Create your models here.

User = get_user_model()



class Post(models.Model):
    """
    A Post model
    """

    class PostType(models.TextChoices):
        text_post = "TextPost"
        visual_post = "VisualPost"
        post_video = "VideoPost"

    text = models.TextField(null=True, blank=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="posts"
    )
    likes = models.ManyToManyField(CustomUser, related_name="post_like", blank=True)
    shared_from = models.ForeignKey(
        "self",
        related_name="shared_by",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    post_type = models.CharField(
        choices=PostType.choices, max_length=50, default=PostType.text_post
    )
    date_created = models.DateTimeField(auto_now_add=True)
    is_edited = models.BooleanField(default=False)

    def __str__(self) -> str:
        return str(self.text)

    def likes_count(self):
        return self.likes.count()

    def comment_count(self):
        return self.comments.count()

    def shares_count(self):
        return self.shared_by.all().count()

    class Meta:
        ordering = ("-date_created",)



class PostPicture(models.Model):
    """
    Post related images, if it has multiple images
    """

    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="pictures"
    )
    image = models.ImageField(upload_to="post_pictures/")

    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return str(self.post)



class PostVideo(models.Model):
    post = models.ForeignKey(
        Post,
        related_name="videos",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    video = models.FileField(upload_to="post_videos/")
    thumbnail = models.FileField(
        upload_to="post_video_thumbnails", null=True, blank=True
    )
    duration = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    date_created = models.DateTimeField(auto_now_add=True)


class PostComment(models.Model):
    """
    A model to store comments by users on a post
    """

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments",
        blank=True,
        null=True,
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="post_comments"
    )
    comment = models.CharField(max_length=200)
    parent = models.ForeignKey(
        "self",
        related_name="sub_comments",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    is_edited = models.BooleanField(default=False)
    likes = models.ManyToManyField(
        User, blank=True, related_name="post_comment_likes"
    )

    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return str(self.post)

    def likes_count(self):
        return self.likes.count()

    class Meta:
        ordering = ("-date_created",)
