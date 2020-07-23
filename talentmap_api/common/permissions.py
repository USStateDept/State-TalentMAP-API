from rest_framework import permissions
from talentmap_api.common.common_helpers import in_group_or_403, in_superuser_group


def isDjangoGroupMember(group_name):
    '''
    Dynamically creates a permission class for the specified group, for use
    in class-based DRF views
    '''

    class IsDjangoGroupMember(permissions.BasePermission):
        def has_permission(self, request, view):
            try:
                in_superuser_group(request.user) or in_group_or_403(request.user, group_name)
                return True
            except BaseException:
                return False

    return IsDjangoGroupMember


def isDjangoGroupMemberOrReadOnly(group_name):
    '''
    Dynamically creates a permission class for the specified group, for use
    in class-based DRF views. Allows use if the user is either hitting a
    read-only endpoint or is in the specified group.
    '''

    class IsDjangoGroupMemberOrReadOnly(permissions.BasePermission):
        def has_permission(self, request, view):
            try:
                in_superuser_group(request.user) or in_group_or_403(request.user, group_name)
                return True
            except BaseException:
                return request.method in permissions.SAFE_METHODS

    return IsDjangoGroupMemberOrReadOnly
