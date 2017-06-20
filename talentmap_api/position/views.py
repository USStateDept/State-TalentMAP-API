from rest_framework.viewsets import ReadOnlyModelViewSet

from talentmap_api.position.models import Position
from talentmap_api.position.filters import PositionFilter
from talentmap_api.position.serializers import PositionSerializer


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
