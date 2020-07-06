from talentmap_api.common.serializers import PrefetchedSerializer
from talentmap_api.integrations.models import SynchronizationJob, SynchronizationTask


class SynchronizationJobSerializer(PrefetchedSerializer):

    class Meta:
        model = SynchronizationJob
        fields = "__all__"
        writable_fields = ('last_synchronization', 'next_synchronization', 'delta_synchronization', 'running', 'talentmap_model', 'priority', 'use_last_date_updated')


class SynchronizationTaskSerializer(PrefetchedSerializer):

    class Meta:
        model = SynchronizationTask
        fields = "__all__"
