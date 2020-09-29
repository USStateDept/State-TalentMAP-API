from rest_framework import serializers
from rest_framework.reverse import reverse
from django.apps import apps

from talentmap_api.common.serializers import PrefetchedSerializer, StaticRepresentationField
from talentmap_api.messaging.models import Notification


class NotificationSerializer(PrefetchedSerializer):
    owner = StaticRepresentationField(read_only=True)

    class Meta:
        model = Notification
        fields = "__all__"
        writable_fields = ("is_read")
