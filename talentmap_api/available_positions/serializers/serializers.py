from talentmap_api.common.serializers import PrefetchedSerializer
from talentmap_api.available_positions.models import AvailablePositionDesignation


class AvailablePositionDesignationSerializer(PrefetchedSerializer):

    class Meta:
        model = model = AvailablePositionDesignation
        fields = "__all__"
        writable_fields = ("is_urgent_vacancy", "is_volunteer", "is_hard_to_fill", "is_highlighted")
