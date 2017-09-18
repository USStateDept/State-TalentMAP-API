from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated

from talentmap_api.common.mixins import ActionDependentSerializerMixin, FieldLimitableSerializerMixin

from talentmap_api.user_profile.models import UserProfile, SavedSearch
from talentmap_api.user_profile.serializers import (UserProfileSerializer,
                                                    UserProfileWritableSerializer,
                                                    SavedSearchSerializer)


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


class SavedSearchView(FieldLimitableSerializerMixin,
                      GenericViewSet,
                      mixins.CreateModelMixin,
                      mixins.ListModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin):
    '''
    create:
    Creates a new saved share

    partial_update:
    Edits a saved share

    retrieve:
    Retrieves a specific saved share

    list:
    Lists all of the user's saved shares

    destroy:
    Deletes a specified saved search
    '''

    serializer_class = SavedSearchSerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user.profile)

    def get_queryset(self):
        queryset = SavedSearch.objects.filter(owner=self.request.user.profile)
        self.serializer_class.prefetch_model(SavedSearch, queryset)
        return queryset
