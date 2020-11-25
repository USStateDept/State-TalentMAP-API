import logging
import coreapi

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.schemas import AutoSchema
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from talentmap_api.cdo.models import AvailableBidders
from talentmap_api.cdo.serializers import (AvailableBiddersSerializer)
import talentmap_api.cdo.services.available_bidders as services
from talentmap_api.cdo.models import AvailableBidders

from talentmap_api.common.permissions import isDjangoGroupMember

logger = logging.getLogger(__name__)


class AvailableBiddersListView(APIView, GenericViewSet):

    permission_classes = (IsAuthenticated, isDjangoGroupMember('cdo'),)
    serializer_class = AvailableBiddersSerializer

    schema = AutoSchema(
        manual_fields=[
            coreapi.Field("page", location='query', type='integer', description='A page number within the paginated result set.'),
            coreapi.Field("limit", location='query', type='integer', description='Number of results to return per page.'),
            coreapi.Field("sort", location='query', type='string', description='a, b, or c'),
        ]
    )

    def get(self, request):
        """
        Return users in Available Bidders list
        """
        return Response(services.get_available_bidders(request.META['HTTP_JWT']))


class AvailableBiddersIdsListView(APIView):

    permission_classes = (IsAuthenticated, isDjangoGroupMember('cdo'),)

    def get(self, request, *args, **kwargs):
        """
        get:
        Return a list of the ids of the users in Available Bidders list
        """
        return Response(AvailableBidders.objects.values_list("bidder_perdet_id", flat=True))


class AvailableBiddersActionView(APIView):
    '''
    add, remove, update an Available Bidder instance
    '''

    permission_classes = (IsAuthenticated, isDjangoGroupMember('cdo'),)

    def put(self, request, pk, format=None):
        '''
        Puts the client in the Available Bidders list
        '''
        return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, pk, format=None):
        '''
        Update's a client in the Available Bidders list
        '''
        return Response(status=status.HTTP_204_NO_CONTENT)

    def delete(self, request, pk, format=None):
        '''
        Removes the client from the Available Bidders list
        '''
        return Response(status=status.HTTP_204_NO_CONTENT)


class AvailableBiddersCSVView(APIView):

    permission_classes = (IsAuthenticated, isDjangoGroupMember('cdo'),)

    def get(self, request, *args, **kwargs):
        """
        Return a list of all of the users in Available Bidders for CSV export
        """
        return services.get_available_bidders_csv(AvailableBidders)
