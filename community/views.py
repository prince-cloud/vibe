from rest_framework.viewsets import ModelViewSet

from .models import (
    Group, 
    Community,
    Announcement
)
from django.http.request import HttpRequest
from .serializers import (
    GroupSerializer,
    GroupCreateSerializer,
    AddGroupMemberSerializer,
    CommunitySerializer,
    CommunityCreateSerializer,
    AddCommunityGroupSerializer
)
from rest_framework import permissions as rest_permissions
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from django.db.models import Q
import logging
from drf_spectacular.utils import extend_schema
from accounts.models import CustomUser
from accounts.serializers import UserInfoSerializer
from rest_framework.exceptions import ValidationError

logger = logging.getLogger(__name__)


class GroupViewSet(ModelViewSet):
    model = Group
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [rest_permissions.IsAuthenticated,]

    def get_serializer_class(self) -> GroupCreateSerializer | GroupSerializer:
        if not self.request.method == "GET":
            return GroupCreateSerializer
        return super().get_serializer_class()
    
    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_authenticated:
            return queryset.none()
        if not self.request.user.is_superuser:
            return queryset.filter(Q(admin=self.request.user) | Q(members__in = self.request.user))
        return queryset

    def perform_create(self, serializer):
        instance = serializer.save(admin=self.request.user)
        instance.members.add(self.request.user)
        instance.save()

    @action(
        methods=["get"],
        detail=True,
        url_path="join",
        url_name="join",
        permission_classes=[rest_permissions.IsAuthenticated],
    )
    def join(self, request: HttpRequest, pk):
        """
        Endpoint to join a group.
        """
        group = get_object_or_404(Group, pk=pk)
        group.members.add(self.request.user)
        group.save()
        serializer = GroupSerializer(
            instance=group, context=self.get_serializer_context()
        )
        return Response(data=serializer.data)
    
    @action(
        methods=["get"],
        detail=True,
        url_path="leave-group",
        url_name="leave-group",
        permission_classes=[rest_permissions.IsAuthenticated],
    )
    def leave_group(self, request: HttpRequest, pk):
        """
        Endpoint to join a group.
        """
        group = get_object_or_404(Group, pk=pk)
        group.members.remove(self.request.user)
        group.save()
        serializer = GroupSerializer(
            instance=group, context=self.get_serializer_context()
        )
        return Response(data=serializer.data)
    
    
    @extend_schema(
        request=AddGroupMemberSerializer,
        responses={"200": GroupSerializer},
    )
    @action(
        methods=["post"],
        detail=True,
        url_path="add-members",
        url_name="add-members",
        permission_classes=[rest_permissions.IsAuthenticated,],
        serializer_class = AddGroupMemberSerializer
    )
    def add_members(self, request: HttpRequest, pk):
        """
        Endpoint to add a member to a group
        """
        group = get_object_or_404(Group, pk=pk)
        if group.admin != request.user:
            raise ValidationError(
                {"error": "Sorry, you are not an admin of this group."}
            )
        members_id = request.data.get("members", [])
        users = CustomUser.objects.filter(id__in=members_id)
        group.members.add(*users)
        group.save()
        serializer = GroupSerializer(
            instance=group, context=self.get_serializer_context()
        )
        return Response(data=serializer.data)
    
    @extend_schema(
        request=AddGroupMemberSerializer,
        responses={"200": GroupSerializer},
    )
    @action(
        methods=["post"],
        detail=True,
        url_path="remove-members",
        url_name="remove-members",
        permission_classes=[rest_permissions.IsAuthenticated,],
        serializer_class = AddGroupMemberSerializer
    )
    def remove_members(self, request: HttpRequest, pk):
        """
        Endpoint to add a member to a group
        """
        group = get_object_or_404(Group, pk=pk)
        if group.admin != request.user:
            raise ValidationError(
                {"error": "Sorry, you are not an admin of this group."}
            )
        members_id = request.data.get("members", [])
        users = CustomUser.objects.filter(id__in=members_id)
        group.members.remove(*users)
        group.save()
        serializer = GroupSerializer(
            instance=group, context=self.get_serializer_context()
        )
        return Response(data=serializer.data)
    

    @action(
        methods=["get"],
        detail=True,
        url_path="get-members",
        url_name="get-members",
        permission_classes=[rest_permissions.IsAuthenticated,],
    )
    def get_members(self, request: HttpRequest, pk):
        """
        Endpoint to get all group members
        """
        group = get_object_or_404(Group, pk=pk)
        users = CustomUser.objects.filter(id__in=[group.members.values_list("id", flat=True)])
        serializer = UserInfoSerializer(
            instance=users, many=True, context=self.get_serializer_context()
        )
        return Response(data=serializer.data)
    

class CommunityViewSet(ModelViewSet):
    model = Community
    queryset = Community.objects.all()
    serializer_class = CommunitySerializer
    permission_classes = [rest_permissions.IsAuthenticated,]

    def get_serializer_class(self) -> CommunityCreateSerializer | CommunitySerializer:
        if not self.request.method == "GET":
            return CommunityCreateSerializer
        return super().get_serializer_class()
    
    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_authenticated:
            return queryset.none()
        if not self.request.user.is_superuser:
            return queryset.filter(Q(admin=self.request.user) | Q(groups__in = self.request.user.group.communities))
        return queryset

    def perform_create(self, serializer):
        instance = serializer.save(admin=self.request.user)
        Announcement.objects.create(name="Announcements", community=instance)
        instance.save()

    @extend_schema(
        request=AddCommunityGroupSerializer,
        responses={"200": CommunitySerializer},
    )
    @action(
        methods=["post"],
        detail=True,
        url_path="add-groups",
        url_name="add-groups",
        permission_classes=[rest_permissions.IsAuthenticated,],
        serializer_class = AddCommunityGroupSerializer
    )
    def add_groups(self, request: HttpRequest, pk):
        """
        Endpoint to add a member to a group
        """
        community = get_object_or_404(Community, pk=pk)
        if community.admin != request.user:
            raise ValidationError(
                {"error": "Sorry, you are not an admin of this community."}
            )
        groups_id = request.data.get("groups", [])
        groups = Group.objects.filter(id__in=groups_id)
        if Group.objects.filter(~Q(admin=request.user), id__in=groups_id,).exists():
            raise ValidationError({"error": "You are not an admin of 1 or more groups you have added"})
        community.groups.add(*groups)
        community.save()
        serializer = CommunitySerializer(
            instance=community, context=self.get_serializer_context()
        )
        return Response(data=serializer.data)
    
    @extend_schema(
        request=AddCommunityGroupSerializer,
        responses={"200": CommunitySerializer},
    )
    @action(
        methods=["post"],
        detail=True,
        url_path="remove-groups",
        url_name="remove-groups",
        permission_classes=[rest_permissions.IsAuthenticated,],
        serializer_class = AddCommunityGroupSerializer
    )
    def remove_groups(self, request: HttpRequest, pk):
        """
        Endpoint to add a member to a group
        """
        community = get_object_or_404(Community, pk=pk)
        if community.admin != request.user:
            raise ValidationError(
                {"error": "Sorry, you are not an admin of this community."}
            )
        groups_id = request.data.get("groups", [])
        groups = Group.objects.filter(id__in=groups_id)
        if Group.objects.filter(~Q(admin=request.user), id__in=groups_id,).exists():
            raise ValidationError({"error": "You are not an admin of 1 or more groups you have added"})
        community.groups.remove(*groups)
        community.save()
        serializer = CommunitySerializer(
            instance=community, context=self.get_serializer_context()
        )
        return Response(data=serializer.data)
    

    @action(
        methods=["get"],
        detail=True,
        url_path="get-groups",
        url_name="get-groups",
        permission_classes=[rest_permissions.IsAuthenticated,],
    )
    def get_groups(self, request: HttpRequest, pk):
        """
        Endpoint to get all group members
        """
        community = get_object_or_404(Community, pk=pk)
        groups = Group.objects.filter(id__in=[community.groups.values_list("id", flat=True)])
        serializer = GroupSerializer(
            instance=groups, many=True, context=self.get_serializer_context()
        )
        return Response(data=serializer.data)