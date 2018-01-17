from talentmap_api.common.serializers import PrefetchedSerializer

from talentmap_api.glossary.models import GlossaryEntry


class GlossaryEntrySerializer(PrefetchedSerializer):

    class Meta:
        model = GlossaryEntry
        fields = "__all__"
