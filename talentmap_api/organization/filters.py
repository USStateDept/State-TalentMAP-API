import rest_framework_filters as filters

from talentmap_api.organization.models import Organization
from talentmap_api.common.filters import ALL_TEXT_LOOKUPS


class OrganizationFilter(filters.FilterSet):
    bureau_organization = filters.RelatedFilter(OrganizationFilter, name='bureau_organization', queryset=Organization.objects.all())
    parent_organization = filters.RelatedFilter(OrganizationFilter, name='bureau_organization', queryset=Organization.objects.all())

    class Meta:
        model = Qualification
        fields = {
            "code": ALL_TEXT_LOOKUPS,
            "long_description": ALL_TEXT_LOOKUPS,
            "short_description": ALL_TEXT_LOOKUPS
        }
