from talentmap_api.common.serializers import PrefetchedSerializer, StaticRepresentationField

from talentmap_api.feedback.models import FeedbackEntry


class FeedbackEntrySerializer(PrefetchedSerializer):
    user = StaticRepresentationField(read_only=True)

    class Meta:
        model = FeedbackEntry
        fields = "__all__"
        writable_fields = ('comments', 'is_interested_in_helping')
