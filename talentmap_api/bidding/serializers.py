from datetime import datetime

from rest_framework import serializers

from talentmap_api.user_profile.serializers import UserProfileSerializer
from talentmap_api.common.serializers import PrefetchedSerializer
from talentmap_api.position.serializers import PositionSerializer
from talentmap_api.bidding.models import BidCycle, Bid, StatusSurvey


class BidCycleSerializer(PrefetchedSerializer):

    def validate(self, data):
        datasource = self.initial_data

        # Convert incoming string dates into date objects for validation
        for date_key in ["cycle_end_date", "cycle_deadline_date", "cycle_start_date"]:
            date = datasource.get(date_key, None)
            if date:
                datasource[date_key] = datetime.strptime(date, '%Y-%m-%d').date()

        # Update our current data if we have any with new data
        if self.instance:
            instance_data = self.instance.__dict__
            instance_data.update(datasource)
            datasource = instance_data

        # Validate our dates are in a chronologically sound order
        if datasource.get("cycle_end_date") < datasource.get("cycle_start_date"):
            raise serializers.ValidationError("Cycle start date must be before cycle end date")
        if datasource.get("cycle_end_date") < datasource.get("cycle_deadline_date"):
            raise serializers.ValidationError("Cycle deadline date must be on or before the cycle end date")
        if datasource.get("cycle_deadline_date") < datasource.get("cycle_start_date"):
            raise serializers.ValidationError("Cycle deadline date must be after cycle start date")

        return data

    class Meta:
        model = BidCycle
        fields = ("id", "name", "cycle_start_date", "cycle_deadline_date", "cycle_end_date", "active")
        writable_fields = ("name", "cycle_start_date", "cycle_deadline_date", "cycle_end_date", "active")


class SurveySerializer(PrefetchedSerializer):

    class Meta:
        model = StatusSurvey
        fields = "__all__"
        writable_fields = ("bidcycle", "is_differential_bidder", "is_fairshare", "is_six_eight")


class BidSerializer(PrefetchedSerializer):
    bidcycle = serializers.StringRelatedField()
    user = serializers.StringRelatedField()
    position = serializers.StringRelatedField()

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
                        "title",
                        "skill",
                        "grade",
                        "post__id",
                        "post__location",
                        "update_date",
                        "create_date"
                    ],
                    "read_only": True
                }
            }
        }


class PositionBidSerializer(PrefetchedSerializer):
    bidcycle = serializers.StringRelatedField()
    user = serializers.StringRelatedField()
    position = serializers.StringRelatedField()

    class Meta:
        model = Bid
        fields = "__all__"
        nested = {
            "user": {
                "class": UserProfileSerializer,
                "field": "user",
                "kwargs": {
                    "override_fields": [
                        "user",
                        "skill_code",
                        "grade"
                    ]
                }
            },
            "position": {
                "class": PositionSerializer,
                "field": "position",
                "kwargs": {
                    "override_fields": [
                        "id",
                        "position_number",
                        "title",
                        "skill",
                        "grade",
                        "post__id",
                        "post__location",
                        "update_date",
                        "create_date"
                    ],
                    "read_only": True
                }
            }
        }


class BidWritableSerializer(PrefetchedSerializer):

    class Meta:
        model = Bid
        fields = ("id", "status")
        writable_fields = ("status")
