import rest_framework_filters as filters

from talentmap_api.bidding.models import BidCycle, Bid, StatusSurvey
from talentmap_api.common.filters import ALL_TEXT_LOOKUPS, DATE_LOOKUPS


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


class StatusSurveyFilter(filters.FilterSet):
    bidcycle = filters.RelatedFilter(BidCycleFilter, name='bidcycle', queryset=BidCycle.objects.all())

    class Meta:
        model = StatusSurvey
        fields = {
            "is_differential_bidder": ["exact"],
            "is_fairshare": ["exact"],
            "is_six_eight": ["exact"]
        }
