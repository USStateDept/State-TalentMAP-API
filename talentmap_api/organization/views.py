from rest_framework.viewsets import ReadOnlyModelViewSet

from talentmap_api.common.common_helpers import get_prefetched_filtered_queryset
from talentmap_api.common.mixins import FieldLimitableSerializerMixin
from talentmap_api.common.history_helpers import generate_historical_view

from talentmap_api.organization.models import Organization, Post, TourOfDuty, Location, Country
from talentmap_api.organization.filters import OrganizationFilter, PostFilter, TourOfDutyFilter, LocationFilter, CountryFilter
from talentmap_api.organization.serializers import OrganizationSerializer, PostSerializer, TourOfDutySerializer, LocationSerializer, CountrySerializer


HistoricalPostView = generate_historical_view(Post, PostSerializer, PostFilter)
HistoricalOrganizationView = generate_historical_view(Organization, OrganizationSerializer, OrganizationFilter)
HistoricalCountryView = generate_historical_view(Country, CountrySerializer, CountryFilter)
HistoricalLocationView = generate_historical_view(Location, LocationSerializer, LocationFilter)
HistoricalTourOfDutyView = generate_historical_view(TourOfDuty, TourOfDutySerializer, TourOfDutyFilter)


class OrganizationListView(FieldLimitableSerializerMixin,
                           ReadOnlyModelViewSet):
    """
    retrieve:
    Return the given organization.

    list:
    Return a list of all organizations.
    """

    serializer_class = OrganizationSerializer
    filter_class = OrganizationFilter

    def get_queryset(self):
        return get_prefetched_filtered_queryset(Organization, self.serializer_class)


class LocationView(FieldLimitableSerializerMixin,
                   ReadOnlyModelViewSet):
    """
    retrieve:
    Return the given location.

    list:
    Return a list of all locations.
    """

    serializer_class = LocationSerializer
    filter_class = LocationFilter

    def get_queryset(self):
        return get_prefetched_filtered_queryset(Location, self.serializer_class)


class CountryView(FieldLimitableSerializerMixin,
                  ReadOnlyModelViewSet):
    """
    retrieve:
    Return the given country.

    list:
    Return a list of all countries.
    """

    serializer_class = CountrySerializer
    filter_class = CountryFilter

    def get_queryset(self):
        return get_prefetched_filtered_queryset(Country, self.serializer_class)


class PostListView(FieldLimitableSerializerMixin,
                   ReadOnlyModelViewSet):
    """
    retrieve:
    Return the given post.

    list:
    Return a list of all posts.
    """

    serializer_class = PostSerializer
    filter_class = PostFilter

    def get_queryset(self):
        return get_prefetched_filtered_queryset(Post, self.serializer_class)


class TourOfDutyListView(FieldLimitableSerializerMixin,
                         ReadOnlyModelViewSet):
    """
    retrieve:
    Return the given tour of duty.

    list:
    Return a list of all tours of duty.
    """

    serializer_class = TourOfDutySerializer
    filter_class = TourOfDutyFilter

    def get_queryset(self):
        return get_prefetched_filtered_queryset(TourOfDuty, self.serializer_class)
