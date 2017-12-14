from datetime import datetime

from rest_framework import serializers

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
                datasource[date_key] = datetime.strptime(date, '%Y-%m-%d').date()

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


class BidPrePanelSerializer(PrefetchedSerializer):
    bidcycle = StaticRepresentationField(read_only=True)
    user = StaticRepresentationField(read_only=True)
    pre_panel = serializers.SerializerMethodField()
    waivers = StaticRepresentationField(read_only=True, many=True)

    def get_pre_panel(self, obj):
        pre_panel = {}

        user = obj.user
        position = obj.position
        waivers = obj.waivers
        sii = user.status_surveys.filter(bidcycle=obj.bidcycle).first()

        if not sii:
            return "Bidder has not submited a self-identification survey for this bidcycle"

        fairshare = {
            "calculated": user.is_fairshare,
            "self_identified": sii.is_fairshare,
            "waivers": [str(x) for x in list(waivers.filter(category=Waiver.Category.fairshare))]
        }

        six_eight = {
            "calculated": user.is_six_eight,
            "self_identified": user.is_six_eight,
            "waivers": [str(x) for x in list(waivers.filter(category=Waiver.Category.six_eight))]
        }

        language_match = True
        reading_proficiency_match = True
        spoken_proficiency_match = True
        for language in list(position.languages.all()):
            user_language = user.language_qualifications.filter(language=language.language).first()
            if not user_language:
                language_match = False
                reading_proficiency_match = False
                spoken_proficiency_match = False
            elif language.reading_proficiency > user_language.reading_proficiency:
                reading_proficiency_match = False
            elif language.spoken_proficiency > user_language.spoken_proficiency:
                spoken_proficiency_match = False

        language = {
            "language_match": language_match,
            "reading_proficiency_match": reading_proficiency_match,
            "spoken_proficiency_match": spoken_proficiency_match,
            "waviers": [str(x) for x in list(waivers.filter(category=Waiver.Category.language))]
        }

        skill = {
            "skill_match": user.skill_code.filter(code=position.skill.code).exists(),
            "waviers": [str(x) for x in list(waivers.filter(category=Waiver.Category.skill))]
        }

        pre_panel['fairshare'] = fairshare
        pre_panel['six_eight'] = six_eight
        pre_panel['language'] = language
        pre_panel['skill'] = skill

        return pre_panel

    class Meta:
        model = Bid
        fields = "__all__"
        nested = {
            "position": {
                "class": PositionSerializer,
                "field": "position",
                "kwargs": {
                    "override_exclude": [
                        "bid_statistics"
                    ],
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
