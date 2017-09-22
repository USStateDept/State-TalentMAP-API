import rest_framework_filters as filters

from talentmap_api.bidding.models import BidCycle
from talentmap_api.common.filters import ALL_TEXT_LOOKUPS, DATE_LOOKUPS


class BidCycleFilter(filters.FilterSet):

    class Meta:
        model = BidCycle
        fields = {
            "name": ALL_TEXT_LOOKUPS,
            "cycle_start_date": DATE_LOOKUPS,
            "cycle_end_date": DATE_LOOKUPS
        }
