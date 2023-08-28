from rest_framework import serializers
from django.http.request import HttpRequest
from django.utils.translation import gettext_lazy as _
from .models import (
    Post,
    PostComment, 
    PostVideo, 
    PostPicture
)

from django.db.models.query import QuerySet
from accounts.serializers import UserInfoSerializer

class PostPictureSerializer(serializers.ModelSerializer):
    """
    A serializer that fetches Posts related images
    """

    class Meta:
        model = PostPicture
        fields = (
            "id",
            "image",
            "post",
        )


class DeletePostPictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostPicture
        fields = ("id",)



class PostVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostVideo
        fields = (
            "id",
            "post",
            "video",
            "thumbnail",
            "duration",
            "date_created",
        )


class PostVideoCreateSerializer(serializers.ModelSerializer):
    video = serializers.FileField()
    thumbnail = serializers.FileField()

    class Meta:
        model = PostVideo
        fields = ("id", "post", "video", "thumbnail", "duration")


class DeletePostVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostVideo
        fields = ("id",)


class PostSerializer(serializers.ModelSerializer):
    """
    A serializer the fetches posts
    """

    pictures = PostPictureSerializer(many=True, read_only=True)

    liked = serializers.SerializerMethodField()

    user_account = UserInfoSerializer() 

    shared_from = serializers.SerializerMethodField(read_only=True)

    videos = PostVideoSerializer(many=True, read_only=True)

    def get_shared_from(self, instance: Post):
        if not instance.shared_from:
            return None
        return PostSerializer(
            instance=instance.shared_from,
            context=self.context,
        ).data

    def get_liked(self, instance: Post):
        """
        check weather the current user liked this particular comment
        """
        request: HttpRequest = self.context.get("request")
        if request.user.is_authenticated:
            return instance.likes.filter(
                id=request.user.id,
            ).exists()

        return False


    class Meta:
        model = Post
        fields = (
            "id",
            "text",
            "user",
            "user_account",
            "liked",
            "likes_count",
            "comment_count",
            "pictures",
            "videos",
            "post_type",
            "shares_count",
            "shared_from", 
            "is_edited",
            "date_created",
        )

        read_only_fields = (
            "user_account",
            "date_created",
            "pictures",
            "videos"
        )

    def validate(self, attrs):
        text = attrs.get("text")
        image = attrs.get("pictures")
        if not text or not image:
            raise serializers.ValidationError(
                _("Post must have a text or pictures")
            )
        attrs = super().validate(attrs)
        return attrs


class PostCreateSerializer(serializers.ModelSerializer):
    """
    A serializer for creating a Post
    """

    pictures = serializers.ListField(
        child=serializers.FileField(),
    )

    def to_representation(self, instance: Post):
        # instance.refresh_from_db()
        return PostSerializer(instance=instance, context=self.context).data

    class Meta:
        model = Post
        fields = (
            "id",
            "text",
            "user",
            "post_type",
            "pictures",
            "videos",
        )

        read_only_fields = ( "user", "date_created", "pictures", "videos")

    def validate_videos(self, videos: list[int]) -> QuerySet[PostVideo]:
        return PostVideo.objects.filter(id__in=videos)


class PostCommentSerializer(serializers.ModelSerializer):
    """
    A serializer for Post comments
    """

    liked = serializers.SerializerMethodField()

    user_account = UserInfoSerializer(read_only=True)

    replies_count = serializers.SerializerMethodField()


    def get_liked(self, instance: PostComment):
        """
        check weather the current user liked this particular comment
        """
        request: HttpRequest = self.context.get("request")
        if request.user.is_authenticated:
            return instance.likes.filter(id=request.user.id).exists()
        return False

    def get_replies_count(self, instance: PostComment):
        return instance.sub_comments.count()


    class Meta:
        model = PostComment
        fields = (
            "id",
            "post",
            "user",
            "user_account",
            "comment",
            "parent",
            "date_created",
            "liked",
            "likes_count",
            "replies_count",
            "is_edited",
        )

        read_only_fields = (
            "user",
            "is_edited",
            "likes_count",
            "date_created",
            "user_account",
        )

    def validate(self, attrs):
        post = attrs.get("post")
        if not post:
            raise serializers.ValidationError(
                _("Comment must have a Post object")
            )
        attrs = super().validate(attrs)
        return attrs

