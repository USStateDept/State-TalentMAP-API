from rest_framework.permissions import IsAuthenticatedOrReadOnly

from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins

from talentmap_api.common.common_helpers import get_prefetched_filtered_queryset
from talentmap_api.common.mixins import FieldLimitableSerializerMixin
from talentmap_api.common.common_helpers import in_group_or_403

from talentmap_api.bidding.models import BidHandshakeCycle
from talentmap_api.bidding.serializers import BidHandshakeCycleSerializer

import logging
logger = logging.getLogger(__name__)


class BidHandshakeCycleView(FieldLimitableSerializerMixin,
                   GenericViewSet,
                   mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.DestroyModelMixin,
                   mixins.UpdateModelMixin):
    """
    retrieve:
    Return the given BidHandshakeCycle entry.

    list:
    Return a list of all BidHandshakeCycle entries.

    partial_update:
    Update a BidHandshakeCycle entry.

    create:
    Creates a BidHandshakeCycle entry.
    """

    serializer_class = BidHandshakeCycleSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def perform_create(self, serializer):
        in_group_or_403(self.request.user, "superuser")
        instance = serializer.save()

    def perform_update(self, serializer):
        in_group_or_403(self.request.user, "superuser")
        instance = serializer.save()
    
    def perform_delete(self, serializer):
        in_group_or_403(self.request.user, "superuser")
        instance = serializer.save()
        instance.delete()

    def get_queryset(self):
        return get_prefetched_filtered_queryset(BidHandshakeCycle, self.serializer_class)
