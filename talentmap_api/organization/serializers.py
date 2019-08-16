from rest_framework import serializers

from talentmap_api.common.serializers import PrefetchedSerializer, StaticRepresentationField
from talentmap_api.organization.models import Organization, Post, TourOfDuty, Location, Country, OrganizationGroup
from talentmap_api.settings import OBC_URL


class OrganizationSerializer(PrefetchedSerializer):
    bureau_organization = serializers.SerializerMethodField()
    parent_organization = serializers.SerializerMethodField()
    groups = StaticRepresentationField(read_only=True, many=True)
    highlighted_positions = StaticRepresentationField(read_only=True, many=True)
    location = StaticRepresentationField(read_only=True)

    # This method returns the string representation of the bureau, or the code
    # if it doesn't currently exist in the database
    def get_bureau_organization(self, obj):
        if obj.bureau_organization:
            return obj.bureau_organization._string_representation
        else:
            return obj._parent_bureau_code

    # This method returns the string representation of the parent org, or the code
    # if it doesn't currently exist in the database
    def get_parent_organization(self, obj):
        if obj.parent_organization:
            return obj.parent_organization._string_representation
        else:
            return obj._parent_organization_code

    class Meta:
        model = Organization
        fields = "__all__"


class OrganizationGroupSerializer(PrefetchedSerializer):
    organizations = StaticRepresentationField(read_only=True, many=True)

    class Meta:
        model = OrganizationGroup
        fields = "__all__"


class CountrySerializer(PrefetchedSerializer):
    country_url = serializers.SerializerMethodField()

    def get_country_url(self, obj):
        if obj.obc_id:
            return f"{OBC_URL}/country/detail/{obj.obc_id}"
        else:
            return None

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
    tour_of_duty = StaticRepresentationField(read_only=True)
    post_overview_url = serializers.SerializerMethodField()
    post_bidding_considerations_url = serializers.SerializerMethodField()

    def get_post_overview_url(self, obj):
        if obj.obc_id:
            return f"{OBC_URL}/post/detail/{obj.obc_id}"
        else:
            return None

    def get_post_bidding_considerations_url(self, obj):
        if obj.obc_id:
            return f"{OBC_URL}/post/postdatadetails/{obj.obc_id}"
        else:
            return None

    class Meta:
        model = Post
        fields = "__all__"
        nested = {
            "location": {
                "class": LocationSerializer,
                "kwargs": {
                    "read_only": True
                }
            }
        }


class TourOfDutySerializer(PrefetchedSerializer):

    class Meta:
        model = TourOfDuty
        fields = "__all__"
