from rest_framework import serializers

from talentmap_api.common.serializers import PrefetchedSerializer, StaticRepresentationField
from talentmap_api.administration.models import HomepageBanner

class HomepageBannerSerializer(PrefetchedSerializer):
    text = StaticRepresentationField(read_only=True)
    is_visible = StaticRepresentationField(read_only=True)

    class Meta:
        model = HomepageBanner
        fields = "__all__"
        writable_fields = ("text", "is_visible",)
