from django.http import HttpRequest
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from .models import (
    Group,
    Community,
)

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = (
            "id",
            "name",
            "admin",
            "members",
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
    class Meta:
        model = Community
        fields = (
            "id",
            "name",
            "admin",
            "announcement",
            "groups",
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

    def validate(self, attrs):
        request: HttpRequest = self.context.get("request")
        groups = attrs.get("groups")
        for group in groups: 
            if group.admin != request.user:
                raise serializers.ValidationError(
                        _("You are not an admin of 1 or more groups you have added")
                    )
        return super().validate(attrs)