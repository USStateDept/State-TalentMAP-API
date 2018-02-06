from talentmap_api.common.serializers import PrefetchedSerializer, StaticRepresentationField

from talentmap_api.glossary.models import GlossaryEntry


class GlossaryEntrySerializer(PrefetchedSerializer):
    last_editing_user = StaticRepresentationField(read_only=True)

    class Meta:
        model = GlossaryEntry
        fields = "__all__"
        writable_fields = ('title', 'definition', 'link')
