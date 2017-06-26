from rest_framework import serializers

from talentmap_api.common.serializers import PrefetchedSerializer
from talentmap_api.organization.models import Organization


class OrganizationSerializer(PrefetchedSerializer):
    bureau_organization = serializers.SerializerMethodField()
    parent_organization = serializers.SerializerMethodField()

    # This method returns the string representation of the bureau, or the code
    # if it doesn't currently exist in the database
    def get_bureau_organization(self, obj):
        if obj.bureau_organization:
            return str(obj.bureau_organization)
        else:
            return obj._parent_bureau_code

    # This method returns the string representation of the parent org, or the code
    # if it doesn't currently exist in the database
    def get_parent_organization(self, obj):
        if obj.parent_organization:
            return str(obj.parent_organization)
        else:
            return obj._parent_organization_code

    class Meta:
        model = Organization
        exclude = ["_parent_bureau_code", "_parent_organization_code"]
