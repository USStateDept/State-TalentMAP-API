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

        prepanel['skill'] = self.generate_prepanel_skill(user, position, waivers)

        return prepanel

        return {
            "reading_proficiency_match": reading_proficiency_match,
            "spoken_proficiency_match": spoken_proficiency_match,
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
