from django.contrib.auth.models import User
import rest_framework_filters as filters

from talentmap_api.bidding.models import Bid

from talentmap_api.user_profile.models import UserProfile

from talentmap_api.common.filters import full_text_search, ALL_TEXT_LOOKUPS, DATE_LOOKUPS, FOREIGN_KEY_LOOKUPS


class UserFilter(filters.FilterSet):

    class Meta:
        model = User
        fields = {
            "first_name": ALL_TEXT_LOOKUPS,
            "last_name": ALL_TEXT_LOOKUPS,
            "username": ALL_TEXT_LOOKUPS
        }


class UserProfileFilter(filters.FilterSet):
    user = filters.RelatedFilter(UserFilter, name='user', queryset=User.objects.all())

    class Meta:
        model = UserProfile
        fields = {
            "user": FOREIGN_KEY_LOOKUPS,
        }


class ClientFilter(UserProfileFilter):
    # Full text search across multiple fields
    q = filters.CharFilter(name="user", method=full_text_search(
        fields=[
            "user__first_name",
            "user__last_name",
            "user__username",
        ]
    ))
