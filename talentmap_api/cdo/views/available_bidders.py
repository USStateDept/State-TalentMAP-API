import logging
import coreapi

from talentmap_api.common.common_helpers import get_prefetched_filtered_queryset


from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.schemas import AutoSchema
from rest_framework.response import Response

from talentmap_api.cdo.models import AvailableBidders
from talentmap_api.cdo.serializers import (AvailableBiddersSerializer)

logger = logging.getLogger(__name__)


class AvailableBiddersListView(APIView):

    permission_classes = (IsAuthenticated,)
    serializer_class = AvailableBiddersSerializer

    print('------------------ In AvailableBiddersListView -------------------------')

    def get(self, idk):
        """
        get:
        Return Available Bidders list
        """
        print(self)
        print(idk)
        print('---------------------------------------------------------------------------')
        return Response({"count": 0, "next": None, "previous": None, "results": [':)']})


class AvailableBiddersIdsListView(APIView):

    permission_classes = (IsAuthenticated,)

    print('----------------- In AvailableBiddersIdsListView!!! -----------------------')

    # how does this all tie together,

    def get(self, request, *args, **kwargs):
        """
        get:
        Return a list of the ids of the users in Available Bidders list
        """
        return Response({"count": 0, "next": None, "previous": None, "results": [':)']})


class AvailableBiddersActionView(APIView):
    '''
    '''

    permission_classes = (IsAuthenticated,)

    print('------------------ In AvailableBiddersActionView -------------------------')

    def get(self, request, pk, format=None):
        print(pk)
        print('---------------------------------------------------------------------------')
        return Response({"count": 0, "next": None, "previous": None, "results": [':)']})


class AvailableBiddersCSVView(APIView):

    permission_classes = (IsAuthenticated,)
    # filter_class = AvailablePositionsFilter

    # schema = AutoSchema(
    #     manual_fields=[
    #     ]
    # )

    def get(self, request, *args, **kwargs):
        """
        Return a list of all of the users for CSV export
        """
        print('------------------ In AvailableBiddersCSVView -------------------------')
        print('---------------------------------------------------------------------------')
        return Response({"count": 0, "next": None, "previous": None, "results": [':)', 'woot!']})
