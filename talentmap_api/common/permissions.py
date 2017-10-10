from rest_framework import permissions
from talentmap_api.common.common_helpers import in_group_or_403
from django.core.exceptions import PermissionDenied


def isDjangoGroupMember(group_name):
    '''
    Dynamically creates a permission class for the specified group, for use
    in class-based DRF views
    '''

    class IsDjangoGroupMember(permissions.BasePermission):
        def has_permission(self, request, view):
            try:
                in_group_or_403(request.user, group_name)
                return True
            except PermissionDenied:
                return False

    return IsDjangoGroupMember
