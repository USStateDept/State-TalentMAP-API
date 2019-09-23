from django.contrib.auth.models import User
import rest_framework_filters as filters

from talentmap_api.bidding.models import Bid, UserBidStatistics
from talentmap_api.bidding.filters import UserBidStatisticsFilter

from talentmap_api.position.models import Grade, Skill
from talentmap_api.position.filters import GradeFilter, SkillFilter

from talentmap_api.language.filters import QualificationFilter
from talentmap_api.language.models import Qualification

from talentmap_api.user_profile.models import UserProfile

from talentmap_api.organization.filters import CountryFilter
from talentmap_api.organization.models import Country

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
    cdo = filters.RelatedFilter('talentmap_api.user_profile.filters.UserProfileFilter', name='cdo', queryset=UserProfile.objects.all())
    grade = filters.RelatedFilter(GradeFilter, name='grade', queryset=Grade.objects.all())
    skills = filters.RelatedFilter(SkillFilter, name='skills', queryset=Skill.objects.all())
    language_qualifications = filters.RelatedFilter(QualificationFilter, name='language_qualifications', queryset=Qualification.objects.all())
    primary_nationality = filters.RelatedFilter(CountryFilter, name="primary_nationality", queryset=Country.objects.all())
    secondary_nationality = filters.RelatedFilter(CountryFilter, name="primary_nationality", queryset=Country.objects.all())

    class Meta:
        model = UserProfile
        fields = {
            "date_of_birth": DATE_LOOKUPS,
            "phone_number": ALL_TEXT_LOOKUPS,
            "user": FOREIGN_KEY_LOOKUPS,
            "cdo": FOREIGN_KEY_LOOKUPS,
            "grade": FOREIGN_KEY_LOOKUPS,
            "skills": FOREIGN_KEY_LOOKUPS,
            "language_qualifications": FOREIGN_KEY_LOOKUPS,
            "primary_nationality": FOREIGN_KEY_LOOKUPS,
            "secondary_nationality": FOREIGN_KEY_LOOKUPS
        }


class ClientFilter(UserProfileFilter):
    bid_statistics = filters.RelatedFilter(UserBidStatisticsFilter, name="bid_statistics", queryset=UserBidStatistics.objects.all())

    is_bidding = filters.BooleanFilter(name="bidlist", method="filter_is_bidding")
    is_in_panel = filters.BooleanFilter(name="bidlist", method="filter_is_in_panel")
    is_bidding_no_handshake = filters.BooleanFilter(name="bidlist", method="filter_is_bidding_no_handshake")

    def filter_is_bidding(self, queryset, name, value):
        value = bool(value)
        if value:
            return queryset.exclude(bidlist=None)
        else:
            return queryset.filter(bidlist=None)

    def filter_is_in_panel(self, queryset, name, value):
        value = bool(value)
        if value:
            return queryset.filter(bidlist__status=Bid.Status.in_panel)
        else:
            return queryset.exclude(bidlist__status=Bid.Status.in_panel)

    def filter_is_bidding_no_handshake(self, queryset, name, value):
        value = bool(value)
        if value:
            return queryset.exclude(bidlist=None).filter(bidlist__handshake_offered_date=None).distinct()
        else:
            return queryset.exclude(bidlist=None).exclude(bidlist__handshake_offered_date=None).distinct()

    # Full text search across multiple fields
    q = filters.CharFilter(name="user", method=full_text_search(
        fields=[
            "user__first_name",
            "user__last_name",
            "user__username",
            "skills__code",
            "skills__description",
            "skills__cone__name",
            "language_qualifications__language__short_description",
            "primary_nationality__name",
            "secondary_nationality__name"
        ]
    ))
