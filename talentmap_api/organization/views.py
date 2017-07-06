from rest_framework.viewsets import ReadOnlyModelViewSet

from talentmap_api.organization.models import Organization, Location, TourOfDuty
from talentmap_api.organization.filters import OrganizationFilter, LocationFilter, TourOfDutyFilter
from talentmap_api.organization.serializers import OrganizationSerializer, LocationSerializer, TourOfDutySerializer


class OrganizationListView(ReadOnlyModelViewSet):
    """
    retrieve:
    Return the given organization.

    list:
    Return a list of all organizations.
    """

    serializer_class = OrganizationSerializer
    filter_class = OrganizationFilter

    def get_queryset(self):
        queryset = Organization.objects.all()
        queryset = self.serializer_class.prefetch_model(Organization, queryset)
        return queryset


class LocationListView(ReadOnlyModelViewSet):
    """
    retrieve:
    Return the given location.

    list:
    Return a list of all locaitons.
    """

    serializer_class = LocationSerializer
    filter_class = LocationFilter

    def get_queryset(self):
        queryset = Location.objects.all()
        queryset = self.serializer_class.prefetch_model(Location, queryset)
        return queryset


class TourOfDutyListView(ReadOnlyModelViewSet):
    """
    retrieve:
    Return the given tour of duty.

    list:
    Return a list of all tours of duty.
    """

    serializer_class = TourOfDutySerializer
    filter_class = TourOfDutyFilter

    def get_queryset(self):
        queryset = TourOfDuty.objects.all()
        queryset = self.serializer_class.prefetch_model(TourOfDuty, queryset)
        return queryset
