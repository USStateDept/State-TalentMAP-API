from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins

from rest_framework.permissions import IsAuthenticatedOrReadOnly

from talentmap_api.common.mixins import FieldLimitableSerializerMixin

from talentmap_api.position.models import CapsuleDescription
from talentmap_api.position.filters import CapsuleDescriptionFilter
from talentmap_api.position.serializers import CapsuleDescriptionSerializer


class CapsuleDescriptionView(FieldLimitableSerializerMixin,
                             GenericViewSet,
                             mixins.CreateModelMixin,
                             mixins.ListModelMixin,
                             mixins.RetrieveModelMixin,
                             mixins.UpdateModelMixin,
                             mixins.DestroyModelMixin):
    '''
    create:
    Creates a new capsule description

    partial_update:
    Edits a saved capsule description

    retrieve:
    Retrieves a specific capsule description

    list:
    Lists all capsule descriptions

    destroy:
    Deletes a specified capsule description
    '''

    serializer_class = CapsuleDescriptionSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_class = CapsuleDescriptionFilter

    def perform_create(self, serializer):
        serializer.save(last_editing_user=self.request.user.profile)

    def perform_update(self, serializer):
        serializer.save(last_editing_user=self.request.user.profile)

    def get_queryset(self):
        queryset = CapsuleDescription.objects.all()
        self.serializer_class.prefetch_model(CapsuleDescription, queryset)
        return queryset
