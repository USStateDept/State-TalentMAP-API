from datetime import datetime

from rest_framework import serializers

from talentmap_api.common.serializers import PrefetchedSerializer, StaticRepresentationField
from talentmap_api.position.models import Position
from talentmap_api.position.serializers import PositionSerializer
from talentmap_api.bidding.models import BidCycle, Bid, StatusSurvey, Waiver

from talentmap_api.user_profile.models import UserProfile
from talentmap_api.user_profile.serializers import UserProfileSerializer


class PrePanelSerializer(PrefetchedSerializer):
    '''
    This is a bit of a bespoke serializer which takes the bid and constructs pre-panel aggregation of statuses and information
    '''
    bidcycle = StaticRepresentationField(read_only=True)
    user = StaticRepresentationField(read_only=True)
    position = StaticRepresentationField(read_only=True)
    prepanel = serializers.SerializerMethodField()

    def get_prepanel(self, obj):
        prepanel = {}

        user = UserProfileSerializer.prefetch_model(UserProfile, UserProfile.objects.all()).get(id=obj.user.id)
        position = PositionSerializer.prefetch_model(Position, Position.objects.all()).get(id=obj.position.id)
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
            "post_location": str(position.post.location),
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
            "position_languages": [str(x) for x in list(position.languages.all())],
            "user_languages": [str(x) for x in list(user.language_qualifications.all())],
            "waviers": [str(x) for x in list(waivers.filter(category=Waiver.Category.language))]
        }

        skill = {
            "skill_match": user.skill_code.filter(code=position.skill.code).exists(),
            "position_skill": str(position.skill),
            "user_skills": [str(x) for x in list(user.skill_code.all())],
            "waviers": [str(x) for x in list(waivers.filter(category=Waiver.Category.skill))]
        }

        prepanel['fairshare'] = fairshare
        prepanel['six_eight'] = six_eight
        prepanel['language'] = language
        prepanel['skill'] = skill

        return prepanel

    class Meta:
        model = Bid
        fields = ("bidcycle", "user", "position", "prepanel")
