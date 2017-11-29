import rest_framework_filters as filters

from talentmap_api.bidding.models import BidCycle, Bid, StatusSurvey, UserBidStatistics
from talentmap_api.common.filters import ALL_TEXT_LOOKUPS, DATE_LOOKUPS, INTEGER_LOOKUPS


class BidCycleFilter(filters.FilterSet):

    class Meta:
        model = BidCycle
        fields = {
            "name": ALL_TEXT_LOOKUPS,
            "cycle_start_date": DATE_LOOKUPS,
            "cycle_end_date": DATE_LOOKUPS
        }


class BidFilter(filters.FilterSet):

    class Meta:
        model = Bid
        fields = {
            "status": ALL_TEXT_LOOKUPS,
            "submission_date": DATE_LOOKUPS,
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
        }


class StatusSurveyFilter(filters.FilterSet):
    bidcycle = filters.RelatedFilter(BidCycleFilter, name='bidcycle', queryset=BidCycle.objects.all())

    class Meta:
        model = StatusSurvey
        fields = {
            "is_differential_bidder": ["exact"],
            "is_fairshare": ["exact"],
            "is_six_eight": ["exact"]
        }
