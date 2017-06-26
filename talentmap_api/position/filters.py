import rest_framework_filters as filters

from talentmap_api.position.models import Position, Grade, Skill

from talentmap_api.language.filters import QualificationFilter
from talentmap_api.language.models import Qualification

from talentmap_api.organization.filters import OrganizationFilter
from talentmap_api.organization.models import Organization

from talentmap_api.common.filters import ALL_TEXT_LOOKUPS, DATE_LOOKUPS


class PositionFilter(filters.FilterSet):
    languages = filters.RelatedFilter(QualificationFilter, name='language_requirements', queryset=Qualification.objects.all())
    grade = filters.RelatedFilter('GradeFilter', name='grade', queryset=Grade.objects.all())
    skill = filters.RelatedFilter('SkillFilter', name='skill', queryset=Skill.objects.all())
    organization = filters.RelatedFilter(OrganizationFilter, name='organization', queryset=Organization.objects.all())
    bureau = filters.RelatedFilter(OrganizationFilter, name='bureau', queryset=Organization.objects.all())

    class Meta:
        model = Position
        fields = {
            "position_number": ALL_TEXT_LOOKUPS,
            "is_overseas": ["exact"],
            "create_date": DATE_LOOKUPS,
            "update_date": DATE_LOOKUPS
        }


class GradeFilter(filters.FilterSet):

    class Meta:
        model = Grade
        fields = {
            "code": ALL_TEXT_LOOKUPS
        }


class SkillFilter(filters.FilterSet):

    class Meta:
        model = Skill
        fields = {
            "code": ALL_TEXT_LOOKUPS,
            "description": ALL_TEXT_LOOKUPS
        }
