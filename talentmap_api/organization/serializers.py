from talentmap_api.common.serializers import PrefetchedSerializer
from talentmap_api.organization.models import Obc


class ObcSerializer(PrefetchedSerializer):

    class Meta:
        model = Obc
        fields = "__all__"
