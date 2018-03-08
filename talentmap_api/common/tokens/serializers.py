from talentmap_api.common.serializers import PrefetchedSerializer
from rest_framework.authtoken.models import Token


class TokenSerializer(PrefetchedSerializer):

    class Meta:
        model = Token
        fields = "__all__"
