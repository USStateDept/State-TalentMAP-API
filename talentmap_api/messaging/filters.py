import rest_framework_filters as filters

from talentmap_api.messaging.models import Notification
from talentmap_api.user_profile.models import UserProfile
from talentmap_api.user_profile.filters import UserProfileFilter
from talentmap_api.common.filters import ALL_TEXT_LOOKUPS, DATE_LOOKUPS, FOREIGN_KEY_LOOKUPS


class NotificationFilter(filters.FilterSet):
    owner = filters.RelatedFilter(UserProfileFilter, name='owner', queryset=UserProfile.objects.all())

    class Meta:
        model = Notification
        fields = {
            "message": ALL_TEXT_LOOKUPS,
            "is_read": ['exact'],
            "date_created": DATE_LOOKUPS,
            "date_updated": DATE_LOOKUPS,
            "owner": FOREIGN_KEY_LOOKUPS
        }
