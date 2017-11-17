from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated

from talentmap_api.common.mixins import ActionDependentSerializerMixin, FieldLimitableSerializerMixin

from talentmap_api.position.models import Assignment
from talentmap_api.user_profile.models import UserProfile
from talentmap_api.position.serializers import AssignmentSerializer
from talentmap_api.user_profile.serializers import (UserProfileSerializer,
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
        queryset = UserProfile.objects.filter(user=self.request.user)
        self.serializer_class.prefetch_model(UserProfile, queryset)
        return queryset.first()


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
        queryset = Assignment.objects.filter(user=self.request.user.profile)
        self.serializer_class.prefetch_model(Assignment, queryset)
        return queryset
