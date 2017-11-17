import datetime
from dateutil.relativedelta import relativedelta

from django.db.models.constants import LOOKUP_SEP
from django.db.models import Q
import rest_framework_filters as filters

from talentmap_api.bidding.models import BidCycle
from talentmap_api.position.models import Position, Grade, Skill, CapsuleDescription, Assignment

from talentmap_api.language.filters import QualificationFilter
from talentmap_api.language.models import Qualification

from talentmap_api.organization.filters import OrganizationFilter, PostFilter, TourOfDutyFilter
from talentmap_api.organization.models import Organization, Post, TourOfDuty

from talentmap_api.common.filters import full_text_search, ALL_TEXT_LOOKUPS, DATE_LOOKUPS


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


class PositionFilter(filters.FilterSet):
    languages = filters.RelatedFilter(QualificationFilter, name='language_requirements', queryset=Qualification.objects.all())
    description = filters.RelatedFilter(CapsuleDescriptionFilter, name='description', queryset=CapsuleDescription.objects.all())
    grade = filters.RelatedFilter(GradeFilter, name='grade', queryset=Grade.objects.all())
    skill = filters.RelatedFilter(SkillFilter, name='skill', queryset=Skill.objects.all())
    organization = filters.RelatedFilter(OrganizationFilter, name='organization', queryset=Organization.objects.all())
    bureau = filters.RelatedFilter(OrganizationFilter, name='bureau', queryset=Organization.objects.all())
    post = filters.RelatedFilter(PostFilter, name='post', queryset=Post.objects.all())
    current_assignment = filters.RelatedFilter('talentmap_api.position.filters.AssignmentFilter', name='current_assignment', queryset=Assignment.objects.all())

    is_domestic = filters.BooleanFilter(name="is_overseas", lookup_expr="exact", exclude=True)
    is_highlighted = filters.BooleanFilter(name="highlighted_by_org", lookup_expr="isnull", exclude=True)

    # Full text search across multiple fields
    q = filters.CharFilter(name="position_number", method=full_text_search(
        fields=[
            "title",
            "organization__long_description",
            "bureau__long_description",
            "skill__description",
            "language_requirements__language__long_description",
            "post__location__code",
            "post__location__country__name",
            "post__location__country__code",
            "post__location__city",
            "post__location__state",
            "description__content"
        ]
    ))

    is_available_in_current_bidcycle = filters.BooleanFilter(name="bid_cycles", method="filter_available_in_current_bidcycle")
    vacancy_in_years = filters.NumberFilter(name="current_assignment__estimated_end_date", method="filter_vacancy_in_years")

    def filter_available_in_current_bidcycle(self, queryset, name, value):
        '''
        Returns a queryset of all positions who are in the latest active bidcycle and do not have any
        bids with handshake or above status
        '''
        # Get latest active bidcycle
        bidcycle = BidCycle.objects.filter(active=True).latest('cycle_start_date')
        return bidcycle.annotated_positions.filter(accepting_bids=value)

    def filter_vacancy_in_years(self, queryset, name, value):
        '''
        Returns a queryset of all positions with a vacancy in the specified number of years
        '''
        start = datetime.datetime.now().date()
        end = start + relativedelta(years=value)
        q_obj = {}
        q_obj[LOOKUP_SEP.join([name, "gt"])] = start
        q_obj[LOOKUP_SEP.join([name, "lte"])] = end
        return queryset.filter(Q(**q_obj))

    class Meta:
        model = Position
        fields = {
            "position_number": ALL_TEXT_LOOKUPS,
            "title": ALL_TEXT_LOOKUPS,
            "is_overseas": ["exact"],
            "create_date": DATE_LOOKUPS,
            "update_date": DATE_LOOKUPS
        }


class AssignmentFilter(filters.FilterSet):
    position = filters.RelatedFilter(PositionFilter, name='position', queryset=Position.objects.all())
    tour_of_duty = filters.RelatedFilter(TourOfDutyFilter, name='position', queryset=TourOfDuty.objects.all())

    class Meta:
        model = Assignment
        fields = {
            "status": ALL_TEXT_LOOKUPS,
            "curtailment_reason": ALL_TEXT_LOOKUPS,
            "create_date": DATE_LOOKUPS,
            "start_date": DATE_LOOKUPS,
            "estimated_end_date": DATE_LOOKUPS,
            "end_date": DATE_LOOKUPS,
            "update_date": DATE_LOOKUPS,
        }
