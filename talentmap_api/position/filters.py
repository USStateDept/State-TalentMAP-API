import rest_framework_filters as filters

from talentmap_api.position.models import Position

from talentmap_api.language.filters import QualificationFilter
from talentmap_api.language.models import Qualification


class PositionFilter(filters.FilterSet):
    languages = filters.RelatedFilter(QualificationFilter, name='language_requirements', queryset=Qualification.objects.all())

    class Meta:
        model = Position
        fields = {}
