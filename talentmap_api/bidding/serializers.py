import maya

from rest_framework import serializers

from talentmap_api.common.serializers import PrefetchedSerializer
from talentmap_api.bidding.models import BidHandshake, BidHandshakeCycle


class BidHandshakeSerializer(PrefetchedSerializer):
    class Meta:
        model = BidHandshake
        fields = "__all__"


# Only use serializer for PUT body data
class BidHandshakeOfferSerializer(PrefetchedSerializer):

    def validate(self, data):
        # The keys can be missing in partial updates
        if "expiration_date" in data:
            if data["expiration_date"] < maya.now().datetime():
                raise serializers.ValidationError({
                    "expiration_date": "Expiration date cannot be earlier than current date (Eastern Time).",
                })
        else:
            data["expiration_date"] = None

        return super(BidHandshakeOfferSerializer, self).validate(data)

    class Meta:
        model = BidHandshake
        fields = "__all__"
        writable_fields = ('expiration_date')


class BidHandshakeCycleSerializer(PrefetchedSerializer):
    class Meta:
        model = BidHandshakeCycle
        fields = "__all__"
        writable_fields = ('cycle_id', 'handshake_allowed_date')