from talentmap_api.common.serializers import PrefetchedSerializer, StaticRepresentationField
from talentmap_api.cdo.models import AvailableBidders


class AvailableBiddersSerializer(PrefetchedSerializer):
    last_editing_user_id = StaticRepresentationField(read_only=True)

    class Meta:
        model = AvailableBidders
        fields = "__all__"
        writable_fields = ('status', 'oc_reason', 'comments', 'is_shared')
