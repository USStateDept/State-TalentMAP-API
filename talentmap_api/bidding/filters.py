import rest_framework_filters as filters

from talentmap_api.bidding.models import BidCycle, Bid, StatusSurvey, UserBidStatistics, Waiver
from talentmap_api.user_profile.models import UserProfile
from talentmap_api.position.models import Position
from talentmap_api.common.filters import ALL_TEXT_LOOKUPS, DATE_LOOKUPS, INTEGER_LOOKUPS, FOREIGN_KEY_LOOKUPS


class BidCycleFilter(filters.FilterSet):

    class Meta:
        model = BidCycle
        fields = {
            "name": ALL_TEXT_LOOKUPS,
            "cycle_start_date": DATE_LOOKUPS,
            "cycle_end_date": DATE_LOOKUPS,
            "active": ["exact"]
        }


class BidFilter(filters.FilterSet):
    waivers = filters.RelatedFilter('talentmap_api.bidding.filters.WaiverFilter', name='waivers', queryset=Waiver.objects.all())

    class Meta:
        model = Bid
        fields = {
            "status": ALL_TEXT_LOOKUPS,
            "draft_date": DATE_LOOKUPS,
            "submitted_date": DATE_LOOKUPS,
            "handshake_offered_date": DATE_LOOKUPS,
            "handshake_accepted_date": DATE_LOOKUPS,
            "in_panel_date": DATE_LOOKUPS,
            "approved_date": DATE_LOOKUPS,
            "declined_date": DATE_LOOKUPS,
            "closed_date": DATE_LOOKUPS,
            "scheduled_panel_date": DATE_LOOKUPS,
        }


class UserBidStatisticsFilter(filters.FilterSet):
    bidcycle = filters.RelatedFilter(BidCycleFilter, name='bidcycle', queryset=BidCycle.objects.all())

    class Meta:
        model = UserBidStatistics
        fields = {
            "draft": INTEGER_LOOKUPS,
            "submitted": INTEGER_LOOKUPS,
            "handshake_offered": INTEGER_LOOKUPS,
            "handshake_accepted": INTEGER_LOOKUPS,
            "in_panel": INTEGER_LOOKUPS,
            "approved": INTEGER_LOOKUPS,
            "declined": INTEGER_LOOKUPS,
            "closed": INTEGER_LOOKUPS,
            "bidcycle": FOREIGN_KEY_LOOKUPS
        }


class StatusSurveyFilter(filters.FilterSet):
    bidcycle = filters.RelatedFilter(BidCycleFilter, name='bidcycle', queryset=BidCycle.objects.all())

    class Meta:
        model = StatusSurvey
        fields = {
            "is_differential_bidder": ["exact"],
            "is_fairshare": ["exact"],
            "is_six_eight": ["exact"],
            "bidcycle": FOREIGN_KEY_LOOKUPS
        }


class WaiverFilter(filters.FilterSet):
    bid = filters.RelatedFilter(BidFilter, name='bid', queryset=Bid.objects.all())
    position = filters.RelatedFilter('talentmap_api.position.filters.PositionFilter', name='position', queryset=Position.objects.all())
    user = filters.RelatedFilter('talentmap_api.user_profile.filters.UserProfileFilter', name='user', queryset=UserProfile.objects.all())

    class Meta:
        model = Waiver
        fields = {
            "user": FOREIGN_KEY_LOOKUPS,
            "position": FOREIGN_KEY_LOOKUPS,
            "bid": FOREIGN_KEY_LOOKUPS,
            "status": ALL_TEXT_LOOKUPS,
            "category": ALL_TEXT_LOOKUPS,
            "type": ALL_TEXT_LOOKUPS,
            "description": ALL_TEXT_LOOKUPS,
            "create_date": DATE_LOOKUPS,
            "update_date": DATE_LOOKUPS
        }
