from rest_framework.viewsets import ModelViewSet

from .models import (
    PostComment,
    PostPicture,
    Post, 
    PostVideo, 
)
from django.http.request import HttpRequest
from .serializers import (
    PostCommentSerializer,
    PostSerializer, 
    PostCreateSerializer,
    PostPictureSerializer, 
    DeletePostPictureSerializer,
    PostVideoSerializer,
    PostVideoCreateSerializer,
    DeletePostVideoSerializer, 
)
from django.db.models.query import QuerySet
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly,
    IsAuthenticated,
)
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from django.db.models import Q
from rest_framework import filters, renderers
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as djangofilters 
import logging

logger = logging.getLogger(__name__)



class PostFilter(djangofilters.FilterSet):
    year = djangofilters.NumberFilter(field_name="published_at__year")
    month = djangofilters.NumberFilter(field_name="published_at__month")
    day = djangofilters.NumberFilter(field_name="published_at__day")

    class Meta:
        model = Post
        fields = (
            "user",
            "shared_by",
            "post_type",
        )


class PostVideoViewset(ModelViewSet):
    parser_classes = (MultiPartParser, FormParser)
    queryset = PostVideo.objects.all()
    serializer_class = PostVideoSerializer
    permission_classes = (IsAuthenticated,)
    filterset_fields = [
        "post",
    ]

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_authenticated:
            return queryset.none()
        return queryset

    def get_serializer_class(
        self,
    ) -> PostVideoCreateSerializer | PostVideoSerializer:
        if not self.request.method == "GET":
            return PostVideoCreateSerializer
        return super().get_serializer_class()

    @action(
        detail=False,
        methods=["post"],
        serializer_class=DeletePostVideoSerializer,
        parser_classes=(JSONParser,),
    )
    def delete(self, request):
        ids = request.data.get("ids", [])
        PostVideo.objects.filter(
            id__in=ids, post__user=request.user
        ).delete()
        return Response(
            {"detail": "Videos, deleted successfully"},
        )



class PostViewSet(ModelViewSet):
    """
    Post serializer ViewSet

    Post upload required either 'picture', 'text-only' or 'text-with-picture'
    a post can have multiple images
    To enable multiple pictures uploads, during post and patch requests, use
    `multipart/form-data` as `content-type`
    """

    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (IsAuthenticated,)
    search_fields = ["text"]
    filter_backends = (filters.SearchFilter, DjangoFilterBackend)
    filterset_class = PostFilter
    renderer_classes = [renderers.JSONRenderer]

    def finalize_response(self, request, response, *args, **kwargs):
        # Set the charset of the response to UTF-8
        response["Content-Type"] = "application/json; charset=utf-8"
        return super().finalize_response(request, response, *args, **kwargs)

    def get_serializer_class(self) -> PostCreateSerializer | PostSerializer:
        if not self.request.method == "GET":
            return PostCreateSerializer
        return super().get_serializer_class()

    def get_queryset(self) -> QuerySet[Post]:
        if not self.request.user.is_authenticated:
            return self.queryset.none()
        return self.queryset

    def perform_create(self, serializer: PostSerializer):
        """
        Creating a Post
        """
        request: HttpRequest = self.request

        
        post = serializer.save(user=self.request.user, pictures=[],)
        for formfile in request.FILES.getlist("pictures"):
            postpic = PostPicture.objects.create(post=post, image=formfile)

        ids = request.data.get("videos")
        if ids:
            PostVideo.objects.filter(id__in=ids).update(post=post)


    def perform_update(self, serializer: PostSerializer):
        """
        Perform Update on a post object
        """
        request: HttpRequest = self.request
        user = self.get_object().user
        post = serializer.save(user=user, pictures=[], is_edited=True, )
        for formfile in request.FILES.getlist("pictures"):
            PostPicture.objects.create(post=post, image=formfile)
        ids = request.data.get("videos")
        if ids:
            PostVideo.objects.filter(id__in=ids).update(post=post)

    @action(
        methods=["get"],
        detail=True,
        url_path="like",
        url_name="like",
        permission_classes=[IsAuthenticated],
    )
    def like(self, request: HttpRequest, pk):
        """
        Endpoint to like a post
        """
        post = get_object_or_404(Post, pk=pk)
        post.likes.add(self.request.user)
        post.save()
        serializer = PostSerializer(
            instance=post, context=self.get_serializer_context()
        )
        return Response(data=serializer.data)
    

    @action(
        methods=["get"],
        detail=True,
        url_path="unlike",
        url_name="unlike",
        permission_classes=[IsAuthenticated],
    )
    def unlike(self, request: HttpRequest, pk):
        """
        Endpoint to unlike a post
        """
        post = get_object_or_404(Post, pk=pk)
        post.likes.remove(self.request.user) 
        post.save()
        serializer = PostSerializer(
            instance=post, context=self.get_serializer_context()
        )
        return Response(data=serializer.data)

    @action(
        methods=["post"],
        detail=True,
        url_path="share",
        url_name="share",
        permission_classes=[IsAuthenticated],
    )
    def share_post(self, request: HttpRequest, pk):
        """
        End point to share Post.
        """
        original_post = get_object_or_404(Post, pk=pk)
        serializer = PostCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        post = serializer.save( shared_from=original_post, user=self.request.user, pictures=[],)
        serializer = PostSerializer(
            instance=post, context=self.get_serializer_context()
        )
        return Response(data=serializer.data)

    @action(
        methods=["get"],
        detail=False,
        url_path="video",
        url_name="video",
        permission_classes=[IsAuthenticated],
    )
    def video(self, request: HttpRequest):
        """
        get rendom post videos
        """
        videos = Post.objects.filter(
            post_type=Post.PostType.post_video,
            videos__isnull=False,
        ).order_by("?").distinct()
        page = self.paginate_queryset(videos)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(videos, many=True)
        return Response(data=serializer.data)


class PostPictureViewSet(ModelViewSet):
    """
    Posts related images, if any

    A post can have multiple images or no images at all
    Posts with multiple images are in the PostPictures model
    """

    parser_classes = (MultiPartParser, FormParser)

    queryset = PostPicture.objects.all()
    serializer_class = PostPictureSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filterset_fields = [
        "post",
    ]

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_authenticated:
            return queryset.none()
        return queryset

    @action(
        detail=False,
        methods=["post"],
        serializer_class=DeletePostPictureSerializer,
        parser_classes=(JSONParser,),
    )
    def delete(self, request):
        ids = request.data.get("ids", [])
        PostPicture.objects.filter(
            id__in=ids, post__user=request.user
        ).delete()
        return Response(
            {"detail": "images, deleted successfully"},
        )


class PostCommentFilter(djangofilters.FilterSet):
    null_parent = djangofilters.BooleanFilter(
        field_name="parent_id", lookup_expr="isnull"
    )

    class Meta:
        model = PostComment
        fields = ("post", "parent", "null_parent")


class PostCommentViewSet(ModelViewSet):
    """
    Post comment
    This viewset enables authenticated users to comment
    on any posts
    """

    queryset = PostComment.objects.all()
    serializer_class = PostCommentSerializer
    permission_classes = (IsAuthenticated,)
    filterset_class = PostCommentFilter
    filter_backends = (
        filters.SearchFilter,
        DjangoFilterBackend,
        filters.OrderingFilter,
    )
    ordering_fields = [
        "date_created",
    ]

    def get_queryset(self):
        """
        Get only comments made my the currnt user on a Post
        if the user is not an admin
        """
        queryset = super().get_queryset()
        if not self.request.user.is_authenticated:
            return queryset.none()
        blocked_users_query = Q(
            user__user_info__blocked_users__user_blocked=self.request.user
        ) | Q(user__user_info__user_blocked__user=self.request.user)
        if not self.request.user.is_superuser:
            queryset = (
                queryset.exclude(blocked_users_query)
                .filter(
                    Q(user=self.request.user)
                    | ~Q(hidden_from__id=self.request.user.id)
                )
                .distinct()
            )
        return queryset

    def perform_create(self, serializer: PostCommentSerializer):
        """Make sure the comment is saved for the current user"""
        return serializer.save(user=self.request.user)
 

    def perform_update(self, serializer):
        """
        set comment edited to True
        """
        instance = serializer.save(user=self.request.user, is_edited=True)

    @action(
        methods=["get"],
        detail=True,
        url_path="like",
        url_name="like",
        permission_classes=[IsAuthenticated],
    )
    def like(self, request: HttpRequest, pk):
        """
        Endpoint to like post comment
        """
        post_comment = get_object_or_404(PostComment, pk=pk)
        post_comment.likes.add(request.user) 
        post_comment.refresh_from_db()
        serializer = PostCommentSerializer(
            instance=post_comment, context=self.get_serializer_context()
        )
        return Response(data=serializer.data)
    
    @action(
        methods=["get"],
        detail=True,
        url_path="unlike",
        url_name="unlike",
        permission_classes=[IsAuthenticated],
    )
    def unlike(self, request: HttpRequest, pk):
        """
        Endpoint to unlike post comments
        """
        post_comment = get_object_or_404(PostComment, pk=pk)

        post_comment.likes.remove(request.user)
        post_comment.save()  
        post_comment.refresh_from_db()
        serializer = PostCommentSerializer(
            instance=post_comment, context=self.get_serializer_context()
        )
        return Response(data=serializer.data)