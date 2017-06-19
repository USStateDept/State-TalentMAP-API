import rest_framework_filters as filters
from django.db.models.constants import LOOKUP_SEP
from django.db.models import Q

from talentmap_api.language.models import Qualification, Proficiency, Language
from talentmap_api.common.filters import ALL_TEXT_LOOKUPS


class LanguageFilter(filters.FilterSet):
    # Convenience filter of "name" which will perform a contains lookup on the description
    name = filters.CharFilter(name="long_description", lookup_expr="contains")

    class Meta:
        model = Language
        fields = {
            "code": ALL_TEXT_LOOKUPS,
            "long_description": ALL_TEXT_LOOKUPS,
            "short_description": ALL_TEXT_LOOKUPS
        }


class ProficiencyFilter(filters.FilterSet):
    at_least = filters.CharFilter(name="code", method="filter_at_least")

    def filter_at_least(self, queryset, name, value):
        '''
        Evaluates if a proficiency is of at least a certain level
        F > X > P > 0 > 0+ . . . 5
        '''
        index = Proficiency.RANKING.index(value)
        valid_ranks = Proficiency.RANKING[index:]
        lookup = LOOKUP_SEP.join([name, "in"])
        return queryset.filter(Q(**{lookup: valid_ranks}))

    class Meta:
        model = Proficiency
        fields = {
            "code": ALL_TEXT_LOOKUPS,
            "description": ALL_TEXT_LOOKUPS
        }


class QualificationFilter(filters.FilterSet):
    language = filters.RelatedFilter(LanguageFilter, name='language', queryset=Language.objects.all())
    written_proficiency = filters.RelatedFilter(ProficiencyFilter, name='written_proficiency', queryset=Proficiency.objects.all())
    spoken_proficiency = filters.RelatedFilter(ProficiencyFilter, name='spoken_proficiency', queryset=Proficiency.objects.all())

    class Meta:
        model = Qualification
        fields = {}
