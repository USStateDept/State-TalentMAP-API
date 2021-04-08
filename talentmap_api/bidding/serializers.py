from talentmap_api.common.serializers import PrefetchedSerializer, StaticRepresentationField
from talentmap_api.bidding.models import BidHandshake


class BidHandshakeSerializer(PrefetchedSerializer):
    class Meta:
        model = BidHandshake
        fields = "__all__"
