from django.shortcuts import get_object_or_404

from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins

from rest_framework.permissions import IsAuthenticatedOrReadOnly

from talentmap_api.common.mixins import FieldLimitableSerializerMixin

from talentmap_api.common.common_helpers import has_permission_or_403

from talentmap_api.position.models import CapsuleDescription
from talentmap_api.position.filters import CapsuleDescriptionFilter
from talentmap_api.position.serializers import CapsuleDescriptionSerializer

class CapsuleDescriptionView(FieldLimitableSerializerMixin,
                             GenericViewSet,
                             mixins.ListModelMixin,
                             mixins.RetrieveModelMixin,
                             mixins.UpdateModelMixin):
    '''
    partial_update:
    Edits a saved capsule description

    retrieve:
    Retrieves a specific capsule description

    list:
    Lists all capsule descriptions
    '''

    serializer_class = CapsuleDescriptionSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_class = CapsuleDescriptionFilter

    def perform_update(self, serializer):
        description = get_object_or_404(CapsuleDescription, pk=self.request.parser_context.get("kwargs").get("pk"))
        has_permission_or_403(self.request.user, f"position.{description.position.post.permission_edit_post_capsule_description_codename}")
        serializer.save(last_editing_user=self.request.user.profile)

    def get_queryset(self):
        queryset = CapsuleDescription.objects.all()
        self.serializer_class.prefetch_model(CapsuleDescription, queryset)
        return queryset
