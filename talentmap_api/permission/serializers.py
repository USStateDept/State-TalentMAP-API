from django.contrib.auth.models import Group, Permission, User

from talentmap_api.common.serializers import PrefetchedSerializer, StaticRepresentationField


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
    user_set = StaticRepresentationField(read_only=True, many=True)

    class Meta:
        model = Group
        fields = "__all__"


class UserPermissionSerializer(PrefetchedSerializer):
    groups = PermissionGroupSerializer(many=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "groups"]
