from rest_framework_bulk import (
    BulkListSerializer,
    BulkSerializerMixin,
)

from talentmap_api.common.serializers import PrefetchedSerializer
from talentmap_api.available_positions.models import AvailablePositionDesignation, AvailablePositionRanking, AvailablePositionRankingLock


class AvailablePositionDesignationSerializer(BulkSerializerMixin, PrefetchedSerializer):

    class Meta:
        model = model = AvailablePositionDesignation
        fields = "__all__"
        writable_fields = ("is_urgent_vacancy", "is_volunteer", "is_hard_to_fill", "is_highlighted")
        list_serializer_class = BulkListSerializer


class AvailablePositionRankingSerializer(PrefetchedSerializer):

    class Meta:
        model = AvailablePositionRanking
        fields = "__all__"
        writable_fields = ("cp_id", "bidder_perdet", "rank")


class AvailablePositionRankingLockSerializer(PrefetchedSerializer):

    class Meta:
        model = AvailablePositionRankingLock
        fields = "__all__"
