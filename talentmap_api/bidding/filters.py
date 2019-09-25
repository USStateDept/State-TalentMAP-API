from django.db.models import Q

import rest_framework_filters as filters

from talentmap_api.bidding.models import BidCycle, Bid, StatusSurvey, UserBidStatistics, Waiver, CyclePosition
from talentmap_api.user_profile.models import UserProfile
from talentmap_api.position.models import Position
from talentmap_api.common.filters import full_text_search, ALL_TEXT_LOOKUPS, DATE_LOOKUPS, INTEGER_LOOKUPS, FOREIGN_KEY_LOOKUPS, NumberInFilter

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


class CyclePositionFilter(filters.FilterSet):
    position = filters.RelatedFilter('talentmap_api.position.filters.PositionFilter', name='position', queryset=Position.objects.all())
    language_codes = filters.Filter(name='language_codes', method="filter_language_codes")
    has_id = NumberInFilter(name='id', lookup_expr='in')
    is_domestic = filters.BooleanFilter(name="position__is_overseas", lookup_expr="exact", exclude=True)
    org_has_groups = NumberInFilter(name='position__organization__groups', lookup_expr='in')

    # Full text search across multiple fields
    q = filters.CharFilter(name="position_number", method=full_text_search(
        fields=[
            "position__title",
            "position__organization__long_description",
            "position__bureau__long_description",
            "position__skill__description",
            "position__skill__code",
            "position__languages__language__long_description",
            "position__languages__language__code",
            "position__post__location__code",
            "position__post__location__country__name",
            "position__post__location__country__code",
            "position__post__location__city",
            "position__post__location__state",
            "position__description__content",
            "position__position_number"
        ]
    ))
    is_available_in_current_bidcycle = filters.Filter(name="no_handshake", method="filter_no_handshake")
    is_available_in_bidcycle = filters.Filter(name="bid_cycles", method="filter_available_in_bidcycle")

    def filter_language_codes(self, queryset, name, value):
        '''
        Returns a queryset of all languages that match the codes provided.
        If NLR is provided, all positions with no language requirement will also be returned
        '''
        langs = value.split(',')
        query = Q(position__languages__language__code__in=langs)
        if 'NLR' in value:
            query = query | Q(position__languages__isnull=True)
        return queryset.filter(query).distinct()

    def filter_no_handshake(self, queryset, name, value):
        return queryset.filter(status_code="OP")

    def filter_available_in_bidcycle(self, queryset, name, value):
        '''
        Returns a queryset of all positions who are in the specified bidcycle(s)
        '''
        return queryset.filter(bidcycle_id__in=value.split(','), bidcycle__active=True, status_code__in=["OP", "HS"])
    
    class Meta:
        model = CyclePosition
        fields = "__all__"