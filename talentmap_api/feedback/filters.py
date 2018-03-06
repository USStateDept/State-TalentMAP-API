import rest_framework_filters as filters

from talentmap_api.feedback.models import FeedbackEntry
from talentmap_api.common.filters import full_text_search, ALL_TEXT_LOOKUPS, FOREIGN_KEY_LOOKUPS, DATETIME_LOOKUPS


class FeedbackEntryFilter(filters.FilterSet):
    q = filters.CharFilter(name="comments", method=full_text_search(
        fields=[
            "comments"
        ]
    ))

    class Meta:
        model = FeedbackEntry
        fields = {
            "comments": ALL_TEXT_LOOKUPS,
            "user": FOREIGN_KEY_LOOKUPS,
            "date_created": DATETIME_LOOKUPS,
            "is_interested_in_helping": ["exact"]
        }
