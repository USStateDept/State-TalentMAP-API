from rest_framework import serializers

from django.contrib.auth.models import Group, Permission

from talentmap_api.common.serializers import PrefetchedSerializer


class PermissionSerializer(PrefetchedSerializer):

    class Meta:
        model = Permission
        fields = ("id", "name", "codename")


class PermissionGroupSerializer(PrefetchedSerializer):
    permissions = PermissionSerializer(many=True)

    class Meta:
        model = Group
        fields = "__all__"


class PermissionGroupMembersSerializer(PrefetchedSerializer):
    permissions = PermissionSerializer(many=True)
    user_set = serializers.StringRelatedField(many=True)

    class Meta:
        model = Group
        fields = "__all__"
