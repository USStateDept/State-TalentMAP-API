from rest_framework import serializers
from rest_framework.reverse import reverse
from django.apps import apps

from talentmap_api.common.serializers import PrefetchedSerializer, StaticRepresentationField
from talentmap_api.integrations.models import SynchronizationJob


class SynchronizationJobSerializer(PrefetchedSerializer):

    class Meta:
        model = SynchronizationJob
        fields = "__all__"
        writable_fields = ('last_synchronization', 'next_synchronization', 'delta_synchronization', 'running', 'talentmap_model', 'priority', 'use_last_date_updated')
