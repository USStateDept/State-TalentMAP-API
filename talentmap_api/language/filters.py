import rest_framework_filters as filters
from django.db.models.constants import LOOKUP_SEP
from django.db.models import Q

from talentmap_api.position.models import Position
from talentmap_api.bidding.models import BidCycle


from talentmap_api.language.models import Qualification, Proficiency, Language
from talentmap_api.common.filters import multi_field_filter, negate_boolean_filter
from talentmap_api.common.filters import ALL_TEXT_LOOKUPS, DATE_LOOKUPS, FOREIGN_KEY_LOOKUPS


class LanguageFilter(filters.FilterSet):
    # Convenience filter of "name" which will perform a contains lookup on the description
    name = filters.CharFilter(name="long_description", lookup_expr="contains")

    is_available = filters.BooleanFilter(name="qualifications__positions", method=negate_boolean_filter("isnull"))

    class Meta:
        model = Language
        fields = {
            "code": ALL_TEXT_LOOKUPS,
            "long_description": ALL_TEXT_LOOKUPS,
            "short_description": ALL_TEXT_LOOKUPS
        }


class ProficiencyFilter(filters.FilterSet):
    at_least = filters.CharFilter(name="code", method="filter_at_least")
    at_most = filters.CharFilter(name="code", method="filter_at_most")

    is_available = filters.BooleanFilter(name="reading_qualifications", method=multi_field_filter(fields=["reading_qualifications", "spoken_qualifications"], lookup_expr="isnull", exclude=True))

    def filter_at_most(self, queryset, name, value):
        '''
        Evaluates if a proficiency is of at most a certain level
        F > X > P > 0 > 0+ . . . 5
        '''
        value = value.replace("plus", "+")
        index = Proficiency.RANKING.index(value) + 1
        valid_ranks = Proficiency.RANKING[:index]
        lookup = LOOKUP_SEP.join([name, "in"])
        return queryset.filter(Q(**{lookup: valid_ranks}))

    def filter_at_least(self, queryset, name, value):
        '''
        Evaluates if a proficiency is of at least a certain level
        F > X > P > 0 > 0+ . . . 5
        '''
        value = value.replace("plus", "+")
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
    reading_proficiency = filters.RelatedFilter(ProficiencyFilter, name='reading_proficiency', queryset=Proficiency.objects.all())
    spoken_proficiency = filters.RelatedFilter(ProficiencyFilter, name='spoken_proficiency', queryset=Proficiency.objects.all())

    is_available = filters.BooleanFilter(name="positions", lookup_expr="isnull", exclude=True)

    class Meta:
        model = Qualification
        fields = {
            "language": FOREIGN_KEY_LOOKUPS,
            "reading_proficiency": FOREIGN_KEY_LOOKUPS,
            "spoken_proficiency": FOREIGN_KEY_LOOKUPS
        }
