from talentmap_api.common.serializers import PrefetchedSerializer
from talentmap_api.bidding.models import BidCycle


class BidCycleSerializer(PrefetchedSerializer):

    class Meta:
        model = BidCycle
        fields = ("id", "name", "cycle_start_date", "cycle_end_date")
        writable_fields = ("name", "cycle_start_date", "cycle_end_date")
