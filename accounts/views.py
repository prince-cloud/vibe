from .models import CustomUser, UserFollowship

# Create your views here.
from rest_framework.viewsets import ModelViewSet
from rest_framework.request import HttpRequest
from django.db import transaction
from rest_framework import permissions as rest_permissions
from . import serializers
from rest_framework.response import Response
from http import HTTPStatus
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken
import typing
from rest_framework.generics import UpdateAPIView
from rest_framework.parsers import MultiPartParser, FormParser

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


class UserViewSet(ModelViewSet):
    """ A viewset for users """
    model = CustomUser
    serializer_class = serializers.UserAccountSerializer
    queryset = CustomUser.objects.all()
    permission_classes = (rest_permissions.IsAuthenticatedOrReadOnly,)

    http_method_names = ["get", "patch", "post"]

    def perform_create(self, serializer: serializers.UserAccountSerializer):
        return serializer.save(instance=self.request.user)

    def perform_update(self, serializer: serializers.UserAccountSerializer):
        return serializer.save(instance=self.request.user)

    @extend_schema(
        request=serializers.EmailEditSerializer,
        responses={"200": serializers.UserAccountSerializer},
    )
    @action(
        methods=["POST"],
        detail=False,
        url_name="update-email",
        url_path="update-email",
        permission_classes=[
            rest_permissions.IsAuthenticated,
        ],
        serializer_class=serializers.EmailEditSerializer,
    )
    def update_email(self, request: HttpRequest):
        user: CustomUser = request.user
        serializer = serializers.EmailEditSerializer(
            data=request.data, instance=user, context=self.get_serializer_context()
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            data=serializers.UserAccountSerializer(
                instance=serializer.instance,
                context=self.get_serializer_context(),
            ).data
        )

    @extend_schema(
        request=None,
        responses={"200": serializers.UserAccountSerializer},
    )
    @action(
        methods=["GET"],
        detail=False,
        url_name="whoami",
        url_path="whoami",
        permission_classes=[
            rest_permissions.IsAuthenticated,
        ],
        serializer_class=serializers.UserAccountSerializer,
    )
    def whoami(
        self,
        request: HttpRequest,
    ) -> Response:
        return Response(self.get_serializer(instance=request.user).data, HTTPStatus.OK)

    


class RegisterViewSet(ModelViewSet):
    """ A viewset for user account registration """
    model = CustomUser
    serializer_class = serializers.UserRegisterSerializer
    queryset = CustomUser.objects.all()
    http_method_names = ("post",)

    def create(self, request: HttpRequest):
        register_serializer = self.serializer_class(data=request.data)
        if register_serializer.is_valid(raise_exception=True):
            self.perform_create(register_serializer)
        token_data: typing.Dict = get_tokens_for_user(register_serializer.instance)
        data: typing.Dict = serializers.UserAccountSerializer(
            register_serializer.instance
        ).data
        data.update(token_data)
        return Response(
            data=serializers.UserAccountSerializerWithToken(
                data, context=self.get_serializer_context()
            ).data,
            status=HTTPStatus.CREATED,
        )

    @transaction.atomic
    def perform_create(self, serializer: serializers.UserRegisterSerializer):
        return serializer.create_user()

    """ An Action to acitvate user account after registration """
    @extend_schema(
        request=serializers.UserActivationSerializer,
        responses={"200": serializers.UserAccountSerializer},
    )
    @action(
        methods=["POST"],
        detail=False,
        url_name="activate",
        url_path="activate",
        serializer_class=serializers.UserAccountSerializer,
    )
    def activate(
        self,
        request: HttpRequest,
    ) -> Response:
        serializer = serializers.UserActivationSerializer(
            data=request.data, context=self.get_serializer_context()
        )
        serializer.is_valid(raise_exception=True)
        user_account = serializer.activate()
        if not user_account:
            return Response(
                {
                    "error": "User Account not found",
                },
                status=HTTPStatus.BAD_REQUEST,
            )
        return Response(self.get_serializer(instance=user_account).data, HTTPStatus.OK)

    """ An action to resent account activation top  """
    @extend_schema(
        request=serializers.ResendAccountTokenSerializer,
        responses={"200": serializers.ResendAccountTokenSerializer},
    )
    @action(
        methods=["POST"],
        detail=False,
        url_name="resend-otp",
        url_path="resend-otp",
        serializer_class=serializers.UserAccountSerializer,
    )
    def resend_otp(self, request, **kwargs):
        serializer = serializers.ResendAccountTokenSerializer(
            data=request.data, context=self.get_serializer_context()
        )
        serializer.is_valid(raise_exception=True)
        serializer.send_token()

        return Response(data=serializer.data, status=HTTPStatus.OK)


class UpdateProfileView(UpdateAPIView):
    """ Updating user profile Viewset """
    serializer_class = serializers.UpdateProfileSerializer
    http_method_names = [
        "patch",
    ]
    permission_classes = [
        rest_permissions.IsAuthenticated,
    ]

    def get_object(self):
        return self.request.user.profile
    

class UpdateProfileImageView(UpdateAPIView):
    """ Update user profile image viewset """
    serializer_class = serializers.ProfileImageSerializer
    http_method_names = [
        "patch",
    ]
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [
        rest_permissions.IsAuthenticated,
    ]

    def get_object(self):
        return self.request.user.profile

class UpdateCoverImageView(UpdateAPIView):
    """ Update user cover image viewset """
    serializer_class = serializers.CoverImageUpageSerializer
    http_method_names = [
        "patch",
    ]
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [
        rest_permissions.IsAuthenticated,
    ]

    def get_object(self):
        return self.request.user.profile


class UserFollowshipViewset(ModelViewSet):
    model = UserFollowship
    serializer_class = serializers.UserFollowshipSerializer
    queryset = UserFollowship.objects.all()
    permission_classes = [rest_permissions.IsAuthenticated,]
    http_method_names = ("get",)
    filterset_fields = ("user",)

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_authenticated:
            return queryset.none()
        return queryset.filter(user=self.request.user)

    @action(
        methods=["get"],
        detail=False,
        url_path="followers",
        url_name="followers",
        permission_classes=[rest_permissions.IsAuthenticated],
    )
    def followers(self, request: HttpRequest,):
        """
        Endpoint get all followers
        """
        followers = UserFollowship.objects.filter(user=self.request.user)
        serializer = serializers.UserFollowshipSerializer(
            instance=followers, many=True, context=self.get_serializer_context()
        )
        return Response(data=serializer.data)
    
    @action(
        methods=["get"],
        detail=False,
        url_path="following",
        url_name="following",
        permission_classes=[rest_permissions.IsAuthenticated],
    )
    def following(self, request: HttpRequest,):
        """
        Endpoint get all followers
        """
        following = UserFollowship.objects.filter(follower=self.request.user)
        serializer = serializers.UserFollowshipSerializer(
            instance=following, many=True, context=self.get_serializer_context()
        )
        return Response(data=serializer.data)