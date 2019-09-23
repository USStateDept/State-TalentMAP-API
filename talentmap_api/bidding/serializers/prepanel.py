from rest_framework import serializers

from talentmap_api.common.common_helpers import safe_navigation
from talentmap_api.common.serializers import PrefetchedSerializer, StaticRepresentationField
from talentmap_api.position.models import Position
from talentmap_api.position.serializers import PositionSerializer
from talentmap_api.bidding.models import Bid, Waiver

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
        position = PositionSerializer.prefetch_model(Position, Position.objects.all()).get(id=obj.position.position.id)
        waivers = obj.waivers
        sii = user.status_surveys.filter(bidcycle=obj.bidcycle).first()

        if not sii:
            return "Bidder has not submitted a self-identification survey for this bidcycle"

        prepanel['language'] = self.generate_prepanel_language(user, position, waivers)
        prepanel['skill'] = self.generate_prepanel_skill(user, position, waivers)

        return prepanel

    def generate_prepanel_language(self, user, position, waivers):
        '''
        For matching the language, we consider a language_match to be true if they possess any
        proficiency in the required language.
        '''

        language_match = True
        reading_proficiency_match = True
        spoken_proficiency_match = True
        for language in list(position.languages.all()):
            user_language = user.language_qualifications.filter(language=language.language).first()
            if user_language:
                reading_proficiency_match = language.reading_proficiency > user_language.reading_proficiency
                spoken_proficiency_match = language.spoken_proficiency > user_language.spoken_proficiency
            else:
                # If we're missing even one language, fail all cases and break
                language_match = False
                reading_proficiency_match = False
                spoken_proficiency_match = False
                break

        return {
            "language_match": language_match,
            "reading_proficiency_match": reading_proficiency_match,
            "spoken_proficiency_match": spoken_proficiency_match,
            "position_languages": [str(x) for x in list(position.languages.all())],
            "user_languages": [str(x) for x in list(user.language_qualifications.all())],
            "waivers": [str(x) for x in list(waivers.filter(category=Waiver.Category.language))]
        }

    def generate_prepanel_skill(self, user, position, waivers):
        return {
            "skill_match": user.skills.filter(code=safe_navigation(position, 'skill.code')).exists(),
            "position_skill": str(safe_navigation(position, 'skill')),
            "user_skills": [str(x) for x in list(user.skills.all())],
            "waivers": [str(x) for x in list(waivers.filter(category=Waiver.Category.skill))]
        }

    class Meta:
        model = Bid
        fields = ("bidcycle", "user", "position", "prepanel")
