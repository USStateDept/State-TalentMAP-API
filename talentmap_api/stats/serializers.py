from talentmap_api.common.serializers import PrefetchedSerializer

from talentmap_api.stats.models import LoginInstance


class LoginInstanceSerializer(PrefetchedSerializer):

    class Meta:
        model = LoginInstance
        fields = ["id", "date_of_login", "details"]
        writable_fields = ("details")
