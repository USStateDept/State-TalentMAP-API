from dateutil.relativedelta import relativedelta

from django.db.models.constants import LOOKUP_SEP
from django.db.models import Q, Subquery
from django.utils import timezone
import rest_framework_filters as filters

from talentmap_api.bidding.models import BidCycle, CyclePosition
from talentmap_api.position.models import Position, Grade, Skill, CapsuleDescription, PositionBidStatistics, SkillCone

from talentmap_api.language.filters import QualificationFilter
from talentmap_api.language.models import Qualification

from talentmap_api.organization.filters import OrganizationFilter, PostFilter, TourOfDutyFilter
from talentmap_api.organization.models import Organization, Post, TourOfDuty

from talentmap_api.common.filters import full_text_search, ALL_TEXT_LOOKUPS, DATE_LOOKUPS, FOREIGN_KEY_LOOKUPS, INTEGER_LOOKUPS, NumberInFilter

import logging
logger = logging.getLogger(__name__)


class GradeFilter(filters.FilterSet):
    is_available = filters.BooleanFilter(name="positions", lookup_expr="isnull", exclude=True)

    class Meta:
        model = Grade
        fields = {
            "code": ALL_TEXT_LOOKUPS
        }


class SkillFilter(filters.FilterSet):
    is_available = filters.BooleanFilter(name="positions", lookup_expr="isnull", exclude=True)
    cone = filters.RelatedFilter('talentmap_api.position.filters.SkillConeFilter', name='cone', queryset=SkillCone.objects.all())

    class Meta:
        model = Skill
        fields = {
            "code": ALL_TEXT_LOOKUPS,
            "description": ALL_TEXT_LOOKUPS,
            "cone": FOREIGN_KEY_LOOKUPS
        }


class SkillConeFilter(filters.FilterSet):
    skills = filters.RelatedFilter(SkillFilter, name='skills', queryset=Skill.objects.all())

    class Meta:
        model = SkillCone
        fields = {
            "name": ALL_TEXT_LOOKUPS,
            "skills": FOREIGN_KEY_LOOKUPS
        }


class CapsuleDescriptionFilter(filters.FilterSet):
    q = filters.CharFilter(name="content", method=full_text_search(
        fields=[
            "content"
        ]
    ))

    class Meta:
        model = CapsuleDescription
        fields = {
            "content": ALL_TEXT_LOOKUPS,
            "date_created": DATE_LOOKUPS,
            "date_updated": DATE_LOOKUPS
        }


class PositionBidStatisticsFilter(filters.FilterSet):
    bidcycle = filters.RelatedFilter('talentmap_api.bidding.filters.BidCycleFilter', name='bidcycle', queryset=BidCycle.objects.all())

    class Meta:
        model = PositionBidStatistics
        fields = {
            "bidcycle": FOREIGN_KEY_LOOKUPS,
            "total_bids": INTEGER_LOOKUPS,
            "in_grade": INTEGER_LOOKUPS,
            "at_skill": INTEGER_LOOKUPS,
            "in_grade_at_skill": INTEGER_LOOKUPS
        }


class PositionFilter(filters.FilterSet):
    languages = filters.RelatedFilter(QualificationFilter, name='languages', queryset=Qualification.objects.all())
    language_codes = filters.Filter(name='language_codes', method="filter_language_codes")
    description = filters.RelatedFilter(CapsuleDescriptionFilter, name='description', queryset=CapsuleDescription.objects.all())
    grade = filters.RelatedFilter(GradeFilter, name='grade', queryset=Grade.objects.all())
    skill = filters.RelatedFilter(SkillFilter, name='skill', queryset=Skill.objects.all())
    organization = filters.RelatedFilter(OrganizationFilter, name='organization', queryset=Organization.objects.all())
    bureau = filters.RelatedFilter(OrganizationFilter, name='bureau', queryset=Organization.objects.all())
    post = filters.RelatedFilter(PostFilter, name='post', queryset=Post.objects.all())
    bid_statistics = filters.RelatedFilter(PositionBidStatisticsFilter, name='bid_statistics', queryset=PositionBidStatistics.objects.all())

    is_domestic = filters.BooleanFilter(name="is_overseas", lookup_expr="exact", exclude=True)
    is_highlighted = filters.BooleanFilter(name="highlighted_by_org", lookup_expr="isnull", exclude=True)
    org_has_groups = NumberInFilter(name='organization__groups', lookup_expr='in')

    # Full text search across multiple fields
    q = filters.CharFilter(name="position_number", method=full_text_search(
        fields=[
            "title",
            "organization__long_description",
            "bureau__long_description",
            "skill__description",
            "skill__code",
            "languages__language__long_description",
            "languages__language__code",
            "post__location__code",
            "post__location__country__name",
            "post__location__country__code",
            "post__location__city",
            "post__location__state",
            "description__content",
            "position_number"
        ]
    ))

    def filter_language_codes(self, queryset, name, value):
        '''
        Returns a queryset of all languages that match the codes provided.
        If NLR is provided, all positions with no language requirement will also be returned
        '''
        langs = value.split(',')
        query = Q(languages__language__code__in=langs)
        if 'NLR' in value:
            query = query | Q(languages__isnull=True)
        return queryset.filter(query).distinct()

    class Meta:
        model = Position
        fields = {
            "position_number": ALL_TEXT_LOOKUPS,
            "title": ALL_TEXT_LOOKUPS,
            "is_overseas": ["exact"],
            "create_date": DATE_LOOKUPS,
            "update_date": DATE_LOOKUPS,
            "effective_date": DATE_LOOKUPS,
            "posted_date": DATE_LOOKUPS,
            "post": FOREIGN_KEY_LOOKUPS,
            "organization": FOREIGN_KEY_LOOKUPS,
            "bureau": FOREIGN_KEY_LOOKUPS,
            "skill": FOREIGN_KEY_LOOKUPS,
            "grade": FOREIGN_KEY_LOOKUPS,
            "description": FOREIGN_KEY_LOOKUPS,
            "languages": FOREIGN_KEY_LOOKUPS,
        }