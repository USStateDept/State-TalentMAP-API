import rest_framework_filters as filters

from talentmap_api.available_positions.models import AvailablePositionRanking, AvailablePositionRankingLock
from talentmap_api.common.filters import ALL_TEXT_LOOKUPS


class AvailablePositionRankingFilter(filters.FilterSet):

    class Meta:
        model = AvailablePositionRanking
        fields = {
            "cp_id": ALL_TEXT_LOOKUPS,
        }


class AvailablePositionRankingLockFilter(filters.FilterSet):

    class Meta:
        model = AvailablePositionRankingLock
        fields = {
            "cp_id": ALL_TEXT_LOOKUPS,
            "bureau_code": ALL_TEXT_LOOKUPS,
            "org_code": ALL_TEXT_LOOKUPS,
        }
