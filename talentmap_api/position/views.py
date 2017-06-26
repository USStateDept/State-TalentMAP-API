from rest_framework.viewsets import ReadOnlyModelViewSet

from talentmap_api.position.models import Position, Grade, Skill
from talentmap_api.position.filters import PositionFilter, GradeFilter, SkillFilter
from talentmap_api.position.serializers import PositionSerializer, GradeSerializer, SkillSerializer


class PositionListView(ReadOnlyModelViewSet):
    """
    Lists all positions.
    """

    serializer_class = PositionSerializer
    filter_class = PositionFilter

    def get_queryset(self):
        queryset = Position.objects.all()
        queryset = self.serializer_class.prefetch_model(Position, queryset)
        return queryset


class GradeListView(ReadOnlyModelViewSet):
        """
        Lists all job grades.
        """

        serializer_class = GradeSerializer
        filter_class = GradeFilter

        def get_queryset(self):
            queryset = Grade.objects.all()
            queryset = self.serializer_class.prefetch_model(Grade, queryset)
            return queryset


class SkillListView(ReadOnlyModelViewSet):
        """
        Lists all job skills.
        """

        serializer_class = SkillSerializer
        filter_class = SkillFilter

        def get_queryset(self):
            queryset = Skill.objects.all()
            queryset = self.serializer_class.prefetch_model(Skill, queryset)
            return queryset
