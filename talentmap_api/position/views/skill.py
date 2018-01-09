from rest_framework.viewsets import ReadOnlyModelViewSet

from talentmap_api.common.common_helpers import get_prefetched_filtered_queryset
from talentmap_api.common.mixins import FieldLimitableSerializerMixin

from talentmap_api.position.models import Skill, SkillCone
from talentmap_api.position.filters import SkillFilter, SkillConeFilter
from talentmap_api.position.serializers import SkillSerializer, SkillConeSerializer


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
    lookup_value_regex = '[0-9]+'

    def get_queryset(self):
        return get_prefetched_filtered_queryset(Skill, self.serializer_class)


class SkillConeView(FieldLimitableSerializerMixin,
                    ReadOnlyModelViewSet):
    """
    retrieve:
    Return the given skill cone.

    list:
    Return a list of all skill cones.
    """

    serializer_class = SkillConeSerializer
    filter_class = SkillConeFilter

    def get_queryset(self):
        return get_prefetched_filtered_queryset(SkillCone, self.serializer_class)
