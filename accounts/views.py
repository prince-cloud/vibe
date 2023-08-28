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
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


class UserViewSet(ModelViewSet):
    """ 
    Userviewset, allowed request: get, post and patch
    this endpoint allows you get all users.
    """
    model = CustomUser
    serializer_class = serializers.UserAccountSerializer
    queryset = CustomUser.objects.all()
    permission_classes = (rest_permissions.IsAuthenticatedOrReadOnly,)
    search_fields = ["first_name", "last_name", "email", "username"]
    filter_backends = (filters.SearchFilter, DjangoFilterBackend)
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
        """
        A view to update user's emaill, authentication is required.
        this views uses current logged in user to perform is this action. 
        """
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

    @action(
        methods=["post"],
        detail=True,
        url_path="follow",
        url_name="follow",
        permission_classes=[rest_permissions.IsAuthenticated],
    )
    def follow(self, request: HttpRequest, pk):
        """
        To follow a user, parse the user ```id``` in the unique integer field.
        if the user exits, the resonse will be "you have successfully followed this user"
        it will return detail not found.
        """
        user = get_object_or_404(CustomUser, pk=pk)
        if not UserFollowship.objects.filter(user=user, follower=self.request.user).exists():
            UserFollowship.objects.create(user=user, follower=self.request.user)
        follow_obj = UserFollowship.objects.get(user=user, follower=self.request.user)
        follow_obj.deleted = False
        follow_obj.save()
        return Response(data={"success":"You have successfully followed this user."})
    
    @action(
        methods=["post"],
        detail=True,
        url_path="unfollow",
        url_name="unfollow",
        permission_classes=[rest_permissions.IsAuthenticated],
    )
    def unfollow(self, request: HttpRequest, pk):
        """
        To follow a user, parse the user ```id``` in the unique integer field.
        if the user exits, the resonse will be "you have successfully followed this user"
        it will return detail not found.
        """
        user = get_object_or_404(CustomUser, pk=pk)
        if not UserFollowship.objects.filter(user=user, follower=self.request.user).exists():
            return Response(data={"error":"You are not following this user."})
        follow_obj = UserFollowship.objects.get(user=user, follower=self.request.user)
        follow_obj.deleted = True
        follow_obj.save()
        return Response(data={"success":"You have successfully unfollowed this user."})

    @extend_schema(
        request=serializers.UserFullProfileSerializer,
        responses={"200": serializers.UserFullProfileSerializer},
    )
    @action(
        methods=["get"],
        detail=False,
        url_name="profile",
        url_path="profile",
        permission_classes=[
            rest_permissions.IsAuthenticated,
        ],  
    )
    def profile(self, request: HttpRequest):
        """
        thie endpoint returns profile of a user, authentications is required,
        it uses current logged in user and fetches the profile information 
        """
        user: CustomUser = get_object_or_404(CustomUser, id=request.user.id)
        serializer = serializers.UserFullProfileSerializer(
            instance=user, many=False, context=self.get_serializer_context()
        ).data
        return Response(data=serializer)

class RegisterViewSet(ModelViewSet):
    """ 
    A viewset for user account registration.
    the ```username```, ```phone_number``` and ```password``` are all required fields.
    an ```otp code``` will be sent to the phone number provided.
    use the ```account activation endpiont``` to activate your account after a successful registration.

    it requires an internet access to send otp, make sure to signup when connected to the internet. 
    """
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
        """ 
        Activate your account with the ```phone_number``` provided at the 
        registration and the ```otp code``` sent to the same phone number.
        """
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
        """
        This endpoint allows you to resend your account activation ```otp```.
        """
        serializer = serializers.ResendAccountTokenSerializer(
            data=request.data, context=self.get_serializer_context()
        )
        serializer.is_valid(raise_exception=True)
        serializer.send_token()
        return Response(data=serializer.data, status=HTTPStatus.OK)


class UpdateProfileView(UpdateAPIView):
    """ 
    To update user's profile information such the ```about``` 
    user need to be authentication perform such action.
    """
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
    """ 
    To update user's profile information such the ```profile image``` 
    user need to be authentication perform such action.
    """
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
    """ 
    To update user's profile information such the ```cover image``` 
    user need to be authentication perform such action.
    """
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
    """
    This view allows to see all users you are ```following``` or 
    users who ```follows```. authentication is required.
    """
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
        This endpoint gets you all of your ```followers```.
        Authententication is required to perform such action.
        """
        followers = UserFollowship.objects.filter(user=self.request.user, deleted=False)
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
        This endpoint gets you users you are```following```.
        Authententication is required to perform such action.
        """
        following = UserFollowship.objects.filter(follower=self.request.user, deleted=False)
        serializer = serializers.UserFollowshipSerializer(
            instance=following, many=True, context=self.get_serializer_context()
        )
        return Response(data=serializer.data)


class UpdateUserPrivacyViewset(ModelViewSet):
    """
    User Data Privacy

    there are two privacies ```Public``` and ```Private```

    ```Private``` hides user info such as ```first_name```, ```last_name```, ```email```, ```total_following```

    """
    queryset = CustomUser.objects.all()
    serializer_class = serializers.UpdatePrivacySerializer
    http_method_names = [
        "patch",
    ]
    permission_classes = [
        rest_permissions.IsAuthenticated,
    ]

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_authenticated:
            return queryset.none()
        return queryset.filter(id=self.request.user.id)

    def perform_create(self, serializer):
        return serializer(user=self.request.user)

