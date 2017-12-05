from rest_framework import serializers

from talentmap_api.common.serializers import PrefetchedSerializer, StaticRepresentationField
from talentmap_api.organization.models import Organization, Post, TourOfDuty, Location, Country


class OrganizationSerializer(PrefetchedSerializer):
    bureau_organization = serializers.SerializerMethodField()
    parent_organization = serializers.SerializerMethodField()
    highlighted_positions = StaticRepresentationField(read_only=True, many=True)
    location = StaticRepresentationField(read_only=True)

    # This method returns the string representation of the bureau, or the code
    # if it doesn't currently exist in the database
    def get_bureau_organization(self, obj):
        if obj.bureau_organization:
            return obj.bureau_organization.string_representation
        else:
            return obj._parent_bureau_code

    # This method returns the string representation of the parent org, or the code
    # if it doesn't currently exist in the database
    def get_parent_organization(self, obj):
        if obj.parent_organization:
            return obj.parent_organization.string_representation
        else:
            return obj._parent_organization_code

    class Meta:
        model = Organization
        fields = "__all__"


class CountrySerializer(PrefetchedSerializer):

    class Meta:
        model = Country
        fields = "__all__"


class LocationSerializer(PrefetchedSerializer):
    country = StaticRepresentationField(read_only=True)

    class Meta:
        model = Location
        fields = "__all__"


class PostSerializer(PrefetchedSerializer):
    code = serializers.CharField(source="_location_code", read_only=True)
    location = StaticRepresentationField(read_only=True)
    tour_of_duty = StaticRepresentationField(read_only=True)

    class Meta:
        model = Post
        fields = "__all__"


class TourOfDutySerializer(PrefetchedSerializer):

    class Meta:
        model = TourOfDuty
        fields = "__all__"
