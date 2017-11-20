from rest_framework.viewsets import ReadOnlyModelViewSet

from talentmap_api.common.common_helpers import get_prefetched_filtered_queryset
from talentmap_api.common.mixins import FieldLimitableSerializerMixin

from talentmap_api.position.models import Skill
from talentmap_api.position.filters import SkillFilter
from talentmap_api.position.serializers import SkillSerializer


class SkillListView(FieldLimitableSerializerMixin,
                    ReadOnlyModelViewSet):
    """
    retrieve:
    Return the given skill.

    list:
    Return a list of all skills.
    """

    serializer_class = SkillSerializer
    filter_class = SkillFilter

    def get_queryset(self):
        return get_prefetched_filtered_queryset(Skill, self.serializer_class)
