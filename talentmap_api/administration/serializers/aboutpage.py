from talentmap_api.common.serializers import PrefetchedSerializer
from talentmap_api.administration.models import AboutPage


class AboutPageSerializer(PrefetchedSerializer):

    class Meta:
        model = AboutPage
        fields = ["content"]
        writable_fields = ("content")
