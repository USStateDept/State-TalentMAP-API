from talentmap_api.common.serializers import PrefetchedSerializer
from talentmap_api.bidding.models import BidHandshake


class BidHandshakeSerializer(PrefetchedSerializer):
    class Meta:
        model = BidHandshake
        fields = "__all__"


# Only use serializer for PUT body data
class BidHandshakeOfferSerializer(PrefetchedSerializer):
    class Meta:
        model = BidHandshake
        fields = "__all__"
        writable_fields = ('expiration_date')