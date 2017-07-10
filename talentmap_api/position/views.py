from rest_framework.viewsets import ReadOnlyModelViewSet

from talentmap_api.position.models import Position, Grade, Skill
from talentmap_api.position.filters import PositionFilter, GradeFilter, SkillFilter
from talentmap_api.position.serializers import PositionSerializer, GradeSerializer, SkillSerializer


class PositionListView(ReadOnlyModelViewSet):
    """
    retrieve:
    Return the given position.

    list:
    Return a list of all positions.
    """

    serializer_class = PositionSerializer
    filter_class = PositionFilter

    def get_queryset(self):
        queryset = Position.objects.all()
        queryset = self.serializer_class.prefetch_model(Position, queryset)
        return queryset


class GradeListView(ReadOnlyModelViewSet):
    """
    retrieve:
    Return the given grade.

    list:
    Return a list of all grades.
    """

    serializer_class = GradeSerializer
    filter_class = GradeFilter

    def get_queryset(self):
        queryset = Grade.objects.all()
        queryset = self.serializer_class.prefetch_model(Grade, queryset)
        return queryset


class SkillListView(ReadOnlyModelViewSet):
    """
    retrieve:
    Return the given skill.

    list:
    Return a list of all skills.
    """

    serializer_class = SkillSerializer
    filter_class = SkillFilter

    def get_queryset(self):
        queryset = Skill.objects.all()
        queryset = self.serializer_class.prefetch_model(Skill, queryset)
        return queryset
