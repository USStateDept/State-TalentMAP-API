from django.shortcuts import get_object_or_404

from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated

from talentmap_api.common.common_helpers import get_prefetched_filtered_queryset
from talentmap_api.common.mixins import ActionDependentSerializerMixin, FieldLimitableSerializerMixin

from talentmap_api.position.models import Assignment
from talentmap_api.user_profile.models import UserProfile
from talentmap_api.position.serializers import AssignmentSerializer
from talentmap_api.user_profile.serializers import (UserProfileSerializer,
                                                    UserProfilePublicSerializer,
                                                    UserProfileWritableSerializer)

from talentmap_api.position.filters import AssignmentFilter


class UserProfileView(FieldLimitableSerializerMixin,
                      mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      ActionDependentSerializerMixin,
                      GenericViewSet):
    """
    retrieve:
    Return the current user profile

    partial_update:
    Update the current user profile
    """
    serializers = {
        "default": UserProfileSerializer,
        "partial_update": UserProfileWritableSerializer
    }

    serializer_class = UserProfileSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return get_prefetched_filtered_queryset(UserProfile, self.serializer_class, user=self.request.user).first()


class UserPublicProfileView(FieldLimitableSerializerMixin,
                            mixins.RetrieveModelMixin,
                            GenericViewSet):
    """
    retrieve:
    Return a specific user profile
    """

    serializer_class = UserProfilePublicSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return get_object_or_404(UserProfile, pk=self.request.parser_context.get("kwargs").get("pk"))


class UserAssignmentHistoryView(FieldLimitableSerializerMixin,
                                GenericViewSet,
                                mixins.ListModelMixin):
    '''
    list:
    Lists all of the user's assignments
    '''

    serializer_class = AssignmentSerializer
    permission_classes = (IsAuthenticated,)
    filter_class = AssignmentFilter

    def get_queryset(self):
        return get_prefetched_filtered_queryset(Assignment, self.serializer_class, user=self.request.user.profile)
