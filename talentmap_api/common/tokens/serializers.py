from talentmap_api.common.serializers import PrefetchedSerializer
from rest_framework_expiring_authtoken.models import ExpiringToken


class TokenSerializer(PrefetchedSerializer):

    class Meta:
        model = ExpiringToken
        fields = "__all__"
