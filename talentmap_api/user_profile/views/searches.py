from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated

from talentmap_api.common.mixins import FieldLimitableSerializerMixin

from talentmap_api.user_profile.models import SavedSearch
from talentmap_api.user_profile.serializers import SavedSearchSerializer


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
