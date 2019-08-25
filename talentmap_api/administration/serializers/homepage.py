from rest_framework import serializers

from talentmap_api.common.serializers import PrefetchedSerializer, StaticRepresentationField
from talentmap_api.administration.models import HomepageBanner


class HomepageBannerSerializer(PrefetchedSerializer):

    class Meta:
        model = HomepageBanner
        fields = ["text", "is_visible"]
        writable_fields = ("text", "is_visible")
