import rest_framework_filters as filters

from talentmap_api.stats.models import LoginInstance
from talentmap_api.common.filters import DATETIME_LOOKUPS


class LoginInstanceFilter(filters.FilterSet):

    class Meta:
        model = LoginInstance
        fields = {
            "date_of_login": DATETIME_LOOKUPS,
        }
