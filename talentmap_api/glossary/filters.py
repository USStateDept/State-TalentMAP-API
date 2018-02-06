import rest_framework_filters as filters

from talentmap_api.glossary.models import GlossaryEntry
from talentmap_api.common.filters import full_text_search, ALL_TEXT_LOOKUPS, FOREIGN_KEY_LOOKUPS, DATETIME_LOOKUPS


class GlossaryEntryFilter(filters.FilterSet):
    q = filters.CharFilter(name="title", method=full_text_search(
        fields=[
            "title",
            "definition",
            "link"
        ]
    ))

    class Meta:
        model = GlossaryEntry
        fields = {
            "title": ALL_TEXT_LOOKUPS,
            "definition": ALL_TEXT_LOOKUPS,
            "link": ALL_TEXT_LOOKUPS,
            "last_editing_user": FOREIGN_KEY_LOOKUPS,
            "date_created": DATETIME_LOOKUPS,
            "date_updated": DATETIME_LOOKUPS
        }
