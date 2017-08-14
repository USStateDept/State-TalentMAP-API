import rest_framework_filters as filters

from talentmap_api.position.models import Position, Grade, Skill

from talentmap_api.language.filters import QualificationFilter
from talentmap_api.language.models import Qualification

from talentmap_api.organization.filters import OrganizationFilter, PostFilter
from talentmap_api.organization.models import Organization, Post

from talentmap_api.common.filters import full_text_search, ALL_TEXT_LOOKUPS, DATE_LOOKUPS, FOREIGN_KEY_LOOKUPS


class GradeFilter(filters.FilterSet):
    is_available = filters.BooleanFilter(name="positions", lookup_expr="isnull", exclude=True)

    class Meta:
        model = Grade
        fields = {
            "code": ALL_TEXT_LOOKUPS
        }


class SkillFilter(filters.FilterSet):
    is_available = filters.BooleanFilter(name="positions", lookup_expr="isnull", exclude=True)

    class Meta:
        model = Skill
        fields = {
            "code": ALL_TEXT_LOOKUPS,
            "description": ALL_TEXT_LOOKUPS
        }


class PositionFilter(filters.FilterSet):
    languages = filters.RelatedFilter(QualificationFilter, name='language_requirements', queryset=Qualification.objects.all())
    grade = filters.RelatedFilter(GradeFilter, name='grade', queryset=Grade.objects.all())
    skill = filters.RelatedFilter(SkillFilter, name='skill', queryset=Skill.objects.all())
    organization = filters.RelatedFilter(OrganizationFilter, name='organization', queryset=Organization.objects.all())
    bureau = filters.RelatedFilter(OrganizationFilter, name='bureau', queryset=Organization.objects.all())
    post = filters.RelatedFilter(PostFilter, name='post', queryset=Post.objects.all())

    is_domestic = filters.BooleanFilter(name="is_overseas", lookup_expr="exact", exclude=True)

    # Full text search across multiple fields
    q = filters.CharFilter(name="position_number", method=full_text_search(
        fields=[
            "title",
            "organization__long_description",
            "bureau__long_description",
            "skill__description",
            "language_requirements__language__long_description",
            "post__location__code",
            "post__location__country",
            "post__location__city",
            "post__location__state",
        ]
    ))

    class Meta:
        model = Position
        fields = {
            "position_number": ALL_TEXT_LOOKUPS,
            "title": ALL_TEXT_LOOKUPS,
            "is_overseas": ["exact"],
            "languages": FOREIGN_KEY_LOOKUPS,
            "grade": FOREIGN_KEY_LOOKUPS,
            "skill": FOREIGN_KEY_LOOKUPS,
            "organization": FOREIGN_KEY_LOOKUPS,
            "bureau": FOREIGN_KEY_LOOKUPS,
            "post": FOREIGN_KEY_LOOKUPS,
            "create_date": DATE_LOOKUPS,
            "update_date": DATE_LOOKUPS
        }
