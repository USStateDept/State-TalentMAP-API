from rest_framework.viewsets import ReadOnlyModelViewSet

from talentmap_api.organization.models import Organization


class OrganizationListView(ReadOnlyModelViewSet):
    """
    Lists all organizations.
    """

    serializer_class = OrganizationSerializer
    filter_class = OrganizationFilter

    def get_queryset(self):
        queryset = Organization.objects.all()
        queryset = self.serializer_class.prefetch_model(Organization, queryset)
        return queryset
