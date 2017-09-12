import rest_framework_filters as filters

from talentmap_api.organization.models import Organization, Post, TourOfDuty, Location
from talentmap_api.common.filters import multi_field_filter, negate_boolean_filter
from talentmap_api.common.filters import ALL_TEXT_LOOKUPS, INTEGER_LOOKUPS, FOREIGN_KEY_LOOKUPS


class OrganizationFilter(filters.FilterSet):
    bureau_organization = filters.RelatedFilter('talentmap_api.organization.filters.OrganizationFilter', name='bureau_organization', queryset=Organization.objects.all())
    parent_organization = filters.RelatedFilter('talentmap_api.organization.filters.OrganizationFilter', name='parent_organization', queryset=Organization.objects.all())
    location = filters.RelatedFilter('talentmap_api.organization.filters.LocationFilter', name='location', queryset=Location.objects.all())

    # Name here must be a valid field, but it is ignored when overriden by the method parameter
    is_available = filters.BooleanFilter(name="bureau_positions", method=multi_field_filter(fields=["bureau_positions", "organization_positions"], lookup_expr="isnull", exclude=True))

    class Meta:
        model = Organization
        fields = {
            "code": ALL_TEXT_LOOKUPS,
            "long_description": ALL_TEXT_LOOKUPS,
            "short_description": ALL_TEXT_LOOKUPS,
            "bureau_organization": FOREIGN_KEY_LOOKUPS,
            "parent_organization": FOREIGN_KEY_LOOKUPS,
            "location": FOREIGN_KEY_LOOKUPS,
            "is_bureau": ['exact'],
            "is_regional": ['exact']
        }


class TourOfDutyFilter(filters.FilterSet):
    is_available = filters.BooleanFilter(name="posts__positions", method=negate_boolean_filter("isnull"))

    class Meta:
        model = TourOfDuty
        fields = {
            "code": ALL_TEXT_LOOKUPS,
            "long_description": ALL_TEXT_LOOKUPS,
            "short_description": ALL_TEXT_LOOKUPS,
            "months": INTEGER_LOOKUPS
        }


class LocationFilter(filters.FilterSet):
    class Meta:
        model = Location
        fields = {
            "code": ALL_TEXT_LOOKUPS,
            "country": ALL_TEXT_LOOKUPS,
            "city": ALL_TEXT_LOOKUPS,
            "state": ALL_TEXT_LOOKUPS
        }


class PostFilter(filters.FilterSet):
    tour_of_duty = filters.RelatedFilter(TourOfDutyFilter, name='tour_of_duty', queryset=TourOfDuty.objects.all())
    location = filters.RelatedFilter(LocationFilter, name='location', queryset=Location.objects.all())

    is_available = filters.BooleanFilter(name="positions", lookup_expr="isnull", exclude=True)

    class Meta:
        model = Post
        fields = {
            "location": FOREIGN_KEY_LOOKUPS,
            "cost_of_living_adjustment": INTEGER_LOOKUPS,
            "differential_rate": INTEGER_LOOKUPS,
            "danger_pay": INTEGER_LOOKUPS,
            "rest_relaxation_point": ALL_TEXT_LOOKUPS,
            "tour_of_duty": FOREIGN_KEY_LOOKUPS,
            "has_consumable_allowance": ["exact"],
            "has_service_needs_differential": ["exact"]
        }
