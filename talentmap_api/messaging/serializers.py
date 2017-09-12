from rest_framework import serializers

from talentmap_api.common.serializers import PrefetchedSerializer
from talentmap_api.messaging.models import Notification


class NotificationSerializer(PrefetchedSerializer):
    owner = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Notification
        fields = "__all__"
        writable_fields = ("is_read")
