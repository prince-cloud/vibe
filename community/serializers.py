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
            "date_created",
        )