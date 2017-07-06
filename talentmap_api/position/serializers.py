from rest_framework import serializers

from talentmap_api.common.serializers import PrefetchedSerializer

from talentmap_api.position.models import Position, Grade, Skill
from talentmap_api.language.serializers import LanguageQualificationSerializer
from talentmap_api.organization.serializers import PostSerializer


class PositionSerializer(PrefetchedSerializer):
    grade = serializers.StringRelatedField()
    skill = serializers.StringRelatedField()
    bureau = serializers.SerializerMethodField()
    organization = serializers.SerializerMethodField()

    # This method returns the string representation of the bureau, or the code
    # if it doesn't currently exist in the database
    def get_bureau(self, obj):
        if obj.bureau:
            return str(obj.bureau)
        else:
            return obj._bureau_code

    # This method returns the string representation of the parent org, or the code
    # if it doesn't currently exist in the database
    def get_organization(self, obj):
        if obj.organization:
            return str(obj.organization)
        else:
            return obj._org_code

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
            },
            "post": {
                "class": PostSerializer,
                "field": "post",
                "kwargs": {
                    "override_fields": [
                        "id",
                        "description"
                    ],
                    "many": False,
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
