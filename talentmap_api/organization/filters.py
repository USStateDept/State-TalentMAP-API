import rest_framework_filters as filters

from django.db.models import Q
from django.db.models.constants import LOOKUP_SEP

from talentmap_api.organization.models import Organization, Post, TourOfDuty
from talentmap_api.common.filters import multi_field_filter, ALL_TEXT_LOOKUPS, INTEGER_LOOKUPS


class OrganizationFilter(filters.FilterSet):
    bureau_organization = filters.RelatedFilter('talentmap_api.organization.filters.OrganizationFilter', name='bureau_organization', queryset=Organization.objects.all())
    parent_organization = filters.RelatedFilter('talentmap_api.organization.filters.OrganizationFilter', name='parent_organization', queryset=Organization.objects.all())

    # Name here must be a valid field, but it is ignored when overriden by the method parameter
    available = filters.BooleanFilter(name="bureau_positions", method=multi_field_filter(fields=["bureau_positions", "organization_positions"], lookup_expr="isnull", exclude=True))

    class Meta:
        model = Organization
        fields = {
            "code": ALL_TEXT_LOOKUPS,
            "long_description": ALL_TEXT_LOOKUPS,
            "short_description": ALL_TEXT_LOOKUPS,
            "is_bureau": ['exact']
        }


class TourOfDutyFilter(filters.FilterSet):
    available = filters.BooleanFilter(name="posts__positions", lookup_expr="isnull", exclude=True)

    class Meta:
        model = TourOfDuty
        fields = {
            "code": ALL_TEXT_LOOKUPS,
            "long_description": ALL_TEXT_LOOKUPS,
            "short_description": ALL_TEXT_LOOKUPS,
            "months": INTEGER_LOOKUPS
        }


class PostFilter(filters.FilterSet):
    tour_of_duty = filters.RelatedFilter(TourOfDutyFilter, name='tour_of_duty', queryset=TourOfDuty.objects.all())

    available = filters.BooleanFilter(name="positions", lookup_expr="isnull", exclude=True)

    class Meta:
        model = Post
        fields = {
            "code": ALL_TEXT_LOOKUPS,
            "description": ALL_TEXT_LOOKUPS,
            "cost_of_living_adjustment": INTEGER_LOOKUPS,
            "differential_rate": INTEGER_LOOKUPS,
            "danger_pay": INTEGER_LOOKUPS,
            "rest_relaxation_point": ALL_TEXT_LOOKUPS,
            "has_consumable_allowance": ["exact"],
            "has_service_needs_differential": ["exact"]
        }
