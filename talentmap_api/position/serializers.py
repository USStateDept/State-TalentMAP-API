from rest_framework import serializers

from talentmap_api.common.serializers import PrefetchedSerializer

from talentmap_api.position.models import Position, Grade, Skill
from talentmap_api.language.serializers import LanguageQualificationSerializer


class PositionSerializer(PrefetchedSerializer):
    grade = serializers.StringRelatedField()
    skill = serializers.StringRelatedField()

    class Meta:
        model = Position
        fields = "__all__"
        nested = {
            "languages": {
                "class": LanguageQualificationSerializer,
                "field": "language_requirements",
                "kwargs": {
                    "many": True,
                    "read_only": True
                }
            }
        }


class GradeSerializer(PrefetchedSerializer):

    class Meta:
        model = Grade
        fields = "__all__"


class SkillSerializer(PrefetchedSerializer):

    class Meta:
        model = Skill
        fields = "__all__"
