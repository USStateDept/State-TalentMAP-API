from rest_framework.viewsets import ViewSet
from rest_framework import status
from rest_framework.response import Response

from django.shortcuts import get_object_or_404

from talentmap_api.common.mixins import FieldLimitableSerializerMixin
from talentmap_api.user_profile.models import UserProfile
from talentmap_api.user_profile.serializers import UserSerializer


class UserPermissionView(FieldLimitableSerializerMixin,
                         ViewSet):
    """
    list:
    Return a list of the current user's permissions.

    retrieve:
    Return the specified user's permissions by profile ID.
    """

    def retrieve(self, request, pk=None, format=None):
        profile = get_object_or_404(UserProfile, id=request.parser_context.get("kwargs").get("pk"))
        return Response(self.construct_return_object(profile.user),
                        status=status.HTTP_200_OK)

    def list(self, request, format=None):
        return Response(self.construct_return_object(request.user),
                        status=status.HTTP_200_OK)

    def construct_return_object(self, user):
        permission_dict = {}
        permission_dict["user"] = UserSerializer(user).data
        permission_dict["groups"] = list(user.groups.values_list("name", flat=True))
        permission_dict["permissions"] = list(user.get_all_permissions())
        return permission_dict
