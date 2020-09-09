import rest_framework_filters as filters

from talentmap_api.stats.models import LoginInstance, ViewPositionInstance
from talentmap_api.common.filters import DATETIME_LOOKUPS, ALL_TEXT_LOOKUPS


class LoginInstanceFilter(filters.FilterSet):

    class Meta:
        model = LoginInstance
        fields = {
            "date_of_login": DATETIME_LOOKUPS,
        }

class ViewPositionInstanceFilter(filters.FilterSet):

    class Meta:
        model = ViewPositionInstance
        fields = {
            "date_of_view": DATETIME_LOOKUPS,
            "position_id": ALL_TEXT_LOOKUPS,
            "position_type": ALL_TEXT_LOOKUPS,
        }
