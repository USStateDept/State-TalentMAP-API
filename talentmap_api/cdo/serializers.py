from talentmap_api.common.serializers import PrefetchedSerializer, StaticRepresentationField
from talentmap_api.cdo.models import AvailableBidders


class AvailableBiddersSerializer(PrefetchedSerializer):
    last_editing_user = StaticRepresentationField(read_only=True)
    update_date = StaticRepresentationField(read_only=True)

    class Meta:
        model = AvailableBidders
        fields = "__all__"
        writable_fields = ('status', 'oc_reason', 'oc_bureau', 'comments', 'is_shared', 'step_letter_one', 'step_letter_two')
