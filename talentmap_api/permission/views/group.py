from rest_framework.viewsets import GenericViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import mixins

from rest_framework.permissions import IsAuthenticated

from django.shortcuts import get_object_or_404
from talentmap_api.common.permissions import isDjangoGroupMember

from django.contrib.auth.models import Group
from talentmap_api.user_profile.models import UserProfile

from talentmap_api.permission.serializers import PermissionGroupSerializer, PermissionGroupMembersSerializer
from talentmap_api.permission.filters import GroupFilter

from talentmap_api.common.mixins import FieldLimitableSerializerMixin, ActionDependentSerializerMixin


class PermissionGroupView(mixins.ListModelMixin,
                          mixins.RetrieveModelMixin,
                          ActionDependentSerializerMixin,
                          FieldLimitableSerializerMixin,
                          GenericViewSet):
    """
    list:
    Return a list of available permission groups.

    retrieve:
    Return the specified permission group details.
    """

    serializers = {
        "default": PermissionGroupSerializer,
        "retrieve": PermissionGroupMembersSerializer
    }

    serializer_class = PermissionGroupSerializer
    filter_class = GroupFilter

    def get_queryset(self):
        queryset = Group.objects.all().order_by("id")
        queryset = self.serializer_class.prefetch_model(Group, queryset)
        return queryset


class PermissionGroupControls(APIView):
    '''
    Controls a permission group's membership
    '''

    permission_classes = (IsAuthenticated, isDjangoGroupMember('bureau_ao'))

    def get(self, request, format=None, **url_arguments):
        '''
        Indicates if the specified user is in the specified group

        Returns 204 if the user is a member, otherwise, 404
        '''
        group = get_object_or_404(Group, id=url_arguments.get("pk"))
        profile = get_object_or_404(UserProfile, id=url_arguments.get("user_id"))

        if group.user_set.filter(profile=profile).exists():
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def put(self, request, format=None, **url_arguments):
        '''
        Adds the specified user to the specified group
        '''
        group = get_object_or_404(Group, id=url_arguments.get("pk"))
        profile = get_object_or_404(UserProfile, id=url_arguments.get("user_id"))

        group.user_set.add(profile.user)

        return Response(status=status.HTTP_204_NO_CONTENT)

    def delete(self, request, format=None, **url_arguments):
        '''
        Removes the specified user from the specified group
        '''
        group = get_object_or_404(Group, id=url_arguments.get("pk"))
        profile = get_object_or_404(UserProfile, id=url_arguments.get("user_id"))

        group.user_set.remove(profile.user)

        return Response(status=status.HTTP_204_NO_CONTENT)
