from rest_framework.viewsets import ReadOnlyModelViewSet

from talentmap_api.common.common_helpers import get_prefetched_filtered_queryset
from talentmap_api.common.mixins import FieldLimitableSerializerMixin

from talentmap_api.glossary.models import GlossaryEntry
from talentmap_api.glossary.filters import GlossaryEntryFilter
from talentmap_api.glossary.serializers import GlossaryEntrySerializer


class GlossaryView(FieldLimitableSerializerMixin,
                   ReadOnlyModelViewSet):
    """
    retrieve:
    Return the given glossary entry.

    list:
    Return a list of all glossary entries.
    """

    serializer_class = GlossaryEntrySerializer
    filter_class = GlossaryEntryFilter

    def get_queryset(self):
        return get_prefetched_filtered_queryset(GlossaryEntry, self.serializer_class)
