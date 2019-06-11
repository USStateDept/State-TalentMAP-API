from rest_framework import serializers

from talentmap_api.common.serializers import PrefetchedSerializer

from talentmap_api.log_viewer.models import LogEntry


class LogEntrySerializer(PrefetchedSerializer):

    class Meta:
        model = LogEntry
        fields = "__all__"
