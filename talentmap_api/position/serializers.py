from talentmap_api.common.serializers import PrefetchedSerializer

from talentmap_api.position.models import Position
from talentmap_api.language.serializers import LanguageQualificationSerializer


class PositionSerializer(PrefetchedSerializer):
    language_requirements = LanguageQualificationSerializer(many=True, read_only=True)

    class Meta:
        model = Position
        fields = "__all__"
        nested = {
            "language_requirements": {
                "class": LanguageQualificationSerializer,
                "field": "language_requirements",
                "kwargs": {
                    "many": True,
                    "read_only": True
                }
            }
        }
