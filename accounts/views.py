from .models import CustomUser

# Create your views here.
from rest_framework.viewsets import ModelViewSet, ViewSet
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


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


class UserViewSet(ModelViewSet):
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
