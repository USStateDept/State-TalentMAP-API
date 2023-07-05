import json

from talentmap_api.common.serializers import PrefetchedSerializer, StaticRepresentationField
from talentmap_api.messaging.models import Notification


class NotificationSerializer(PrefetchedSerializer):
    owner = StaticRepresentationField(read_only=True)

    class Meta:
        model = Notification
        fields = "__all__"
        writable_fields = ("is_read")


    def to_representation(self, data):
        data = super(NotificationSerializer, self).to_representation(data)
        try:
            data['meta'] = json.loads(data.get('meta'))
            return data
        except:
            return {}
