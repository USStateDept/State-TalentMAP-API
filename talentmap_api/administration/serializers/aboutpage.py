from rest_framework import serializers

from talentmap_api.common.serializers import PrefetchedSerializer, StaticRepresentationField
from talentmap_api.administration.models import AboutPage

class AboutPageSerializer(PrefetchedSerializer):

    class Meta:
        model = AboutPage
        fields = ["content"]
        writable_fields = ("content")
