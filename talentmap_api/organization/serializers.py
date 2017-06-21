from rest_framework import serializers

from talentmap_api.common.serializers import PrefetchedSerializer
from talentmap_api.organization import Organization


class OrganizationSerializer(PrefetchedSerializer):
    bureau_organization = serializers.StringRelatedField()
    parent_organization = serializers.StringRelatedField()

    class Meta:
        model = Organization
        fields = "__all__"
        exclude = ["_parent_bureau_code", "_parent_organization_code"]
