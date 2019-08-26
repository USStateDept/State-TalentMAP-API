from datetime import datetime

from rest_framework import serializers

from talentmap_api.common.common_helpers import ensure_date
from talentmap_api.common.serializers import PrefetchedSerializer, StaticRepresentationField
from talentmap_api.position.serializers import PositionSerializer, PositionBidStatisticsSerializer, LanguageQualificationSerializer, PostSerializer, CapsuleDescriptionSerializer, CurrentAssignmentSerializer
from talentmap_api.bidding.models import BidCycle, Bid, StatusSurvey, UserBidStatistics, Waiver, CyclePosition
from talentmap_api.position.models import Position

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
        fields = ("id", "name", "cycle_start_date", "cycle_deadline_date", "cycle_end_date", "active", "_cycle_status")
        writable_fields = ("name", "cycle_start_date", "cycle_deadline_date", "cycle_end_date", "active", "_cycle_status")


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


class CyclePositionSerializer(PrefetchedSerializer):
    status = StaticRepresentationField(read_only=True)
    status_code = StaticRepresentationField(read_only=True)
    ted = StaticRepresentationField(read_only=True)
    posted_date = StaticRepresentationField(read_only=True)
    availability = serializers.SerializerMethodField()

    def get_availability(self, obj):
        return obj.availability

    class Meta:
        model = CyclePosition
        fields = "__all__"
        nested = {
            "position": {
                "class": PositionSerializer,
                "field": "position",
                "kwargs": {
                    "many": False,
                    "read_only": True
                }
            },
            "bid_statistics": {
                "class": PositionBidStatisticsSerializer,
                "kwargs": {
                    "read_only": True
                }
            },
            "languages": {
                "class": LanguageQualificationSerializer,
                "kwargs": {
                    "many": True,
                    "read_only": True
                }
            },
            "post": {
                "class": PostSerializer,
                "field": "post",
                "kwargs": {
                    "many": False,
                    "read_only": True
                }
            },
            "description": {
                "class": CapsuleDescriptionSerializer,
                "field": "description",
                "kwargs": {
                    "read_only": True
                }
            },
            "bidcycle": {
                "class": "talentmap_api.bidding.serializers.serializers.BidCycleSerializer",
                "field": "bidcycle",
                "kwargs": {
                    "read_only": True
                }
            },
            "current_assignment": {
                "class": CurrentAssignmentSerializer,
                "field": "current_assignment",
                "kwargs": {
                    "override_fields": [
                        "user",
                        "status",
                        "start_date",
                        "tour_of_duty",
                        "estimated_end_date"
                    ],
                    "read_only": True
                }
            }
        }


class BidSerializer(PrefetchedSerializer):
    bidcycle = StaticRepresentationField(read_only=True)
    user = StaticRepresentationField(read_only=True)
    emp_id = StaticRepresentationField(read_only=True)
    position = StaticRepresentationField(read_only=True)
    waivers = StaticRepresentationField(read_only=True, many=True)
    is_paneling_today = serializers.BooleanField(read_only=True)
    can_delete = serializers.BooleanField(read_only=True)

    class Meta:
        model = Bid
        fields = "__all__"
        nested = {
            "position": {
                "class": CyclePositionSerializer,
                "field": "position",
                "kwargs": {
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

class CyclePositionListSerializer(PrefetchedSerializer):
    status = StaticRepresentationField(read_only=True)
    status_code = StaticRepresentationField(read_only=True)
    ted = StaticRepresentationField(read_only=True)
    posted_date = StaticRepresentationField(read_only=True)
    availability = serializers.SerializerMethodField()

    def get_availability(self, obj):
        return obj.availability

    class Meta:
        model = CyclePosition
        fields = ["id", "status", "status_code", "ted", "posted_date", "availability", "is_urgent_vacancy", "is_volunteer", "is_hard_to_fill"]
        nested = {
            "position": {
                "class": "talentmap_api.position.serializers.PositionSerializer",
                "kwargs": {
                    "read_only": True
                }
            },
            "bidcycle": {
                "class": "talentmap_api.bidding.serializers.serializers.BidCycleSerializer",
                "kwargs": {
                    "read_only": True
                }
            },
            "bid_statistics": {
                "class": "talentmap_api.position.serializers.PositionBidStatisticsSerializer",
                "kwargs": {
                    "read_only": True
                }
            },
            "bid_cycle_statuses": {
                "class": CyclePositionSerializer,
                "kwargs": {
                    "many": True,
                    "read_only": True
                }
            }
        }

class CyclePositionDesignationSerializer(PrefetchedSerializer):

    class Meta:
        model = model = CyclePosition
        fields = "__all__"
        writable_fields = ("is_urgent_vacancy", "is_volunteer", "is_hard_to_fill")