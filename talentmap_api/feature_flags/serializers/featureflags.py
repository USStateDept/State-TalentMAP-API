from rest_framework import serializers

from talentmap_api.common.serializers import PrefetchedSerializer, StaticRepresentationField
from talentmap_api.feature_flags.models import FeatureFlags


class FeatureFlagsSerializer(PrefetchedSerializer):

    class Meta:
        model = FeatureFlags
        fields = ["feature_flags", "date_updated"]
        writable_fields = ("feature_flags")
