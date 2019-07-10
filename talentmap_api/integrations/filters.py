import rest_framework_filters as filters

from talentmap_api.integrations.models import SynchronizationJob
from talentmap_api.common.filters import full_text_search, ALL_TEXT_LOOKUPS, FOREIGN_KEY_LOOKUPS, DATETIME_LOOKUPS


class SynchronizationJobFilter(filters.FilterSet):

    class Meta:
        model = SynchronizationJob
        fields = {
            "last_synchronization": DATETIME_LOOKUPS,
            "next_synchronization": DATETIME_LOOKUPS,
            "delta_synchronization": ALL_TEXT_LOOKUPS,
            "running": ALL_TEXT_LOOKUPS,
            "talentmap_model": ALL_TEXT_LOOKUPS,
            "priority": ALL_TEXT_LOOKUPS,
            "use_last_date_updated": ALL_TEXT_LOOKUPS
        }
