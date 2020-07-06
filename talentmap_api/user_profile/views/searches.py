from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated

from talentmap_api.common.common_helpers import get_prefetched_filtered_queryset
from talentmap_api.common.mixins import FieldLimitableSerializerMixin

from talentmap_api.user_profile.models import SavedSearch
from talentmap_api.user_profile.serializers import SavedSearchSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly


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
        serializer.save(owner=self.request.user.profile, jwt_token=self.request.META['HTTP_JWT'])

    def perform_update(self, serializer):
        serializer.save(owner=self.request.user.profile, jwt_token=self.request.META['HTTP_JWT'])

    def get_queryset(self):
        return get_prefetched_filtered_queryset(SavedSearch, self.serializer_class, owner=self.request.user.profile)


class SavedSearchListCountView(APIView):

    permission_classes = (IsAuthenticatedOrReadOnly,)

    @classmethod
    def get_extra_actions(cls):
        return []

    def put(self, request, *args, **kwargs):

        SavedSearch.update_counts_for_endpoint(contains=True, jwt_token=request.META['HTTP_JWT'], user=request.user.profile)
        return Response(status=status.HTTP_204_NO_CONTENT)
