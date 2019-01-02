from datetime import datetime

from rest_framework import serializers

from talentmap_api.common.common_helpers import ensure_date
from talentmap_api.common.serializers import PrefetchedSerializer, StaticRepresentationField
from talentmap_api.position.serializers import PositionSerializer
from talentmap_api.bidding.models import BidCycle, Bid, StatusSurvey, UserBidStatistics, Waiver


class BidCycleSerializer(PrefetchedSerializer):

    def validate(self, data):
        datasource = self.initial_data

        # Convert incoming string dates into date objects for validation
        for date_key in ["cycle_end_date", "cycle_deadline_date", "cycle_start_date"]:
            date = datasource.get(date_key, None)
            if date:
                datasource[date_key] = ensure_date(date)

        # Update our current data if we have any with new data
        if self.instance:
            instance_data = self.instance.__dict__
            instance_data.update(datasource)
            datasource = instance_data

        # Validate our dates are in a chronologically sound order
        start_date = datasource.get("cycle_start_date")
        end_date = datasource.get("cycle_end_date")
        deadline_date = datasource.get("cycle_deadline_date")

        if end_date < start_date:
            raise serializers.ValidationError("Cycle start date must be before cycle end date")
        if end_date < deadline_date:
            raise serializers.ValidationError("Cycle deadline date must be on or before the cycle end date")
        if deadline_date < start_date:
            raise serializers.ValidationError("Cycle deadline date must be after cycle start date")

        return data

    class Meta:
        model = BidCycle
        fields = ("id", "name", "cycle_start_date", "cycle_deadline_date", "cycle_end_date", "active")
        writable_fields = ("name", "cycle_start_date", "cycle_deadline_date", "cycle_end_date", "active")


class BidCycleStatisticsSerializer(PrefetchedSerializer):
    total_positions = serializers.SerializerMethodField()
    available_positions = serializers.SerializerMethodField()
    available_domestic_positions = serializers.SerializerMethodField()
    available_international_positions = serializers.SerializerMethodField()
    total_bids = serializers.SerializerMethodField()
    total_bidders = serializers.SerializerMethodField()
    approved_bidders = serializers.SerializerMethodField()
    in_panel_bidders = serializers.SerializerMethodField()
    bidding_days_remaining = serializers.SerializerMethodField()

    def get_total_positions(self, obj):
        return obj.positions.count()

    def get_available_positions(self, obj):
        return obj.annotated_positions.filter(accepting_bids=True).count()

    def get_available_domestic_positions(self, obj):
        return obj.annotated_positions.filter(accepting_bids=True, post__location__country__code="USA").count()

    def get_available_international_positions(self, obj):
        return obj.annotated_positions.filter(accepting_bids=True).exclude(post__location__country__code="USA").count()

    def get_total_bids(self, obj):
        return obj.bids.count()

    def get_total_bidders(self, obj):
        return obj.bids.values('user').distinct().count()

    def get_in_panel_bidders(self, obj):
        return obj.bids.filter(status=Bid.Status.in_panel).values('user').distinct().count()

    def get_approved_bidders(self, obj):
        return obj.bids.filter(status=Bid.Status.approved).values('user').distinct().count()

    def get_bidding_days_remaining(self, obj):
        return (obj.cycle_deadline_date.date() - datetime.now().date()).days

    class Meta:
        model = BidCycle
        fields = ("id", "name", "cycle_start_date", "cycle_deadline_date", "cycle_end_date",
                  "total_positions", "available_positions", "available_domestic_positions", "available_international_positions",
                  "total_bids", "total_bidders", "in_panel_bidders", "approved_bidders", "bidding_days_remaining",)


class SurveySerializer(PrefetchedSerializer):
    calculated_values = serializers.SerializerMethodField()

    def get_calculated_values(self, obj):
        calculated_values = {}
        calculated_values['is_fairshare'] = obj.user.is_fairshare
        calculated_values['is_six_eight'] = obj.user.is_six_eight

        return calculated_values

    class Meta:
        model = StatusSurvey
        fields = "__all__"
        writable_fields = ("bidcycle", "is_differential_bidder", "is_fairshare", "is_six_eight")


class BidSerializer(PrefetchedSerializer):
    bidcycle = StaticRepresentationField(read_only=True)
    user = StaticRepresentationField(read_only=True)
    position = StaticRepresentationField(read_only=True)
    waivers = StaticRepresentationField(read_only=True, many=True)
    is_paneling_today = serializers.BooleanField(read_only=True)
    can_delete = serializers.BooleanField(read_only=True)

    class Meta:
        model = Bid
        fields = "__all__"
        nested = {
            "position": {
                "class": PositionSerializer,
                "field": "position",
                "kwargs": {
                    "override_fields": [
                        "id",
                        "position_number",
                        "bureau",
                        "title",
                        "skill",
                        "grade",
                        "post__id",
                        "post__location",
                        "update_date",
                        "create_date",
                        "bid_statistics"
                    ],
                    "read_only": True
                }
            },
            "reviewer": {
                "class": "talentmap_api.user_profile.serializers.UserProfileShortSerializer",
                "field": "reviewer",
                "kwargs": {
                    "read_only": True
                }
            }
        }


class UserBidStatisticsSerializer(PrefetchedSerializer):
    bidcycle = StaticRepresentationField(read_only=True)
    user = StaticRepresentationField(read_only=True)

    class Meta:
        model = UserBidStatistics
        fields = "__all__"


class BidWritableSerializer(PrefetchedSerializer):
    '''
    This is only used by AOs to schedule the panel date
    '''

    def validate(self, data):
        datasource = self.initial_data

        # Convert incoming string dates into date objects for validation
        date = datasource.get('scheduled_panel_date', None)
        if date:
            datasource['scheduled_panel_date'] = ensure_date(date)

        # Update our current data if we have any with new data
        if self.instance:
            instance_data = self.instance.__dict__
            instance_data.update(datasource)
            datasource = instance_data

        return data

    class Meta:
        model = Bid
        fields = ("id", "scheduled_panel_date")
        writable_fields = ("scheduled_panel_date")


class WaiverSerializer(PrefetchedSerializer):
    '''
    For read-only usages
    '''
    bid = StaticRepresentationField(read_only=True)
    user = StaticRepresentationField(read_only=True)
    reviewer = StaticRepresentationField(read_only=True)
    position = StaticRepresentationField(read_only=True)

    class Meta:
        model = Waiver
        fields = "__all__"


class WaiverClientSerializer(PrefetchedSerializer):
    '''
    For client/CDO creation (no status editing)
    '''

    class Meta:
        model = Waiver
        fields = "__all__"
        writable_fields = ("bid", "position", "type", "category", "description")
