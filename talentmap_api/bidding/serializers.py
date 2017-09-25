from rest_framework import serializers

from talentmap_api.common.serializers import PrefetchedSerializer
from talentmap_api.bidding.models import BidCycle, Bid


class BidCycleSerializer(PrefetchedSerializer):

    class Meta:
        model = BidCycle
        fields = ("id", "name", "cycle_start_date", "cycle_end_date", "active")
        writable_fields = ("name", "cycle_start_date", "cycle_end_date", "active")


class BidSerializer(PrefetchedSerializer):
    bidcycle = serializers.StringRelatedField()
    user = serializers.StringRelatedField()
    position = serializers.StringRelatedField()

    class Meta:
        model = Bid
        fields = "__all__"
