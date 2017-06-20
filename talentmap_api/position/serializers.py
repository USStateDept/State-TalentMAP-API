from talentmap_api.common.serializers import PrefetchedSerializer

from talentmap_api.position.models import Position
from talentmap_api.language.serializers import LanguageQualificationSerializer


class PositionSerializer(PrefetchedSerializer):

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
