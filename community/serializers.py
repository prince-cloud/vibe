from django.http import HttpRequest
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from .models import (
    Group,
    Community,
)
from accounts.models import CustomUser

class GroupSerializer(serializers.ModelSerializer):
    total_members = serializers.SerializerMethodField()

    def get_total_members(self, instance: Group):
        return instance.members.count()
    
    class Meta:
        model = Group
        fields = (
            "id",
            "name",
            "admin",
            "members",
            "total_members",
            "profile_picture",
            "date_created",
        )


class GroupCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = (
            "name",
        )


class AddGroupMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = (
            "members", 
        )
 


class CommunitySerializer(serializers.ModelSerializer):
    total_groups = serializers.SerializerMethodField()
    total_members = serializers.SerializerMethodField()

    def get_total_groups(self, instance: Community):
        return instance.groups.count()
    
    def get_total_members(self, instance: Community):
        return CustomUser.objects.filter(group__community=instance).count()
    
    class Meta:
        model = Community
        fields = (
            "id",
            "name",
            "admin",
            "announcement",
            "groups",
            "total_groups",
            "total_members",
            "profile_picture",
            "date_created",
        )


class CommunityCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Community
        fields = (
            "name",
            "groups"
        )

    def validate(self, attrs):
        request: HttpRequest = self.context.get("request")
        groups = attrs.get("groups")
        for group in groups: 
            if group.admin != request.user:
                raise serializers.ValidationError(
                        _("You are not an admin of 1 or more groups you have added")
                    )
                
        return super().validate(attrs)


class AddCommunityGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Community
        fields = (
            "groups",
        )