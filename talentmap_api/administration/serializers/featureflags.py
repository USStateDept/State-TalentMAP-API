from rest_framework import serializers

from talentmap_api.common.serializers import PrefetchedSerializer, StaticRepresentationField
from talentmap_api.administration.models import FeatureFlags


class FeatureFlagsSerializer(PrefetchedSerializer):

    class Meta:
        model = FeatureFlags
        fields = ["content"]
        writable_fields = ("content")
