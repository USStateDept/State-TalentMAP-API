from rest_framework.viewsets import ReadOnlyModelViewSet

from talentmap_api.common.mixins import FieldLimitableSerializerMixin

from talentmap_api.position.models import Grade
from talentmap_api.position.filters import GradeFilter
from talentmap_api.position.serializers import GradeSerializer


class GradeListView(FieldLimitableSerializerMixin,
                    ReadOnlyModelViewSet):
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
