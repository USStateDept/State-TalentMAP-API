from rest_framework import serializers

from talentmap_api.common.serializers import PrefetchedSerializer
from talentmap_api.organization.models import Obc
from talentmap_api.settings import OBC_URL


class ObcSerializer(PrefetchedSerializer):

    class Meta:
        model = Obc
        fields = "__all__"
