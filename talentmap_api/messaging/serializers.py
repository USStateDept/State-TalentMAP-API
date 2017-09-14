from rest_framework import serializers
from rest_framework.reverse import reverse
from django.apps import apps

from talentmap_api.common.serializers import PrefetchedSerializer
from talentmap_api.messaging.models import Notification, Sharable


class NotificationSerializer(PrefetchedSerializer):
    owner = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Notification
        fields = "__all__"
        writable_fields = ("is_read")


class SharableSerializer(PrefetchedSerializer):
    sharing_user = serializers.StringRelatedField(read_only=True)
    receiving_user = serializers.StringRelatedField(read_only=True)

    content = serializers.SerializerMethodField()

    def get_content(self, obj):
        model = apps.get_model(obj.sharable_model)
        instance = model.objects.get(id=obj.sharable_id)

        return {
            "representation": f"{instance}",
            "url": reverse(f'{obj.sharable_model}-detail', kwargs={"pk": obj.sharable_id}, request=self.context.get("request"))
        }

    class Meta:
        model = Sharable
        fields = ["id", "sharing_user", "receiving_user", "content", "is_read"]
        writable_fields = ("is_read",)
