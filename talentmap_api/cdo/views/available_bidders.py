import logging
import coreapi
from django.shortcuts import get_object_or_404
from datetime import datetime

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from talentmap_api.cdo.serializers import AvailableBiddersSerializer
import talentmap_api.cdo.services.available_bidders as services
from talentmap_api.cdo.models import AvailableBidders

from talentmap_api.user_profile.models import UserProfile

from talentmap_api.common.mixins import FieldLimitableSerializerMixin
from talentmap_api.common.common_helpers import in_group_or_403
from talentmap_api.common.permissions import isDjangoGroupMember
import talentmap_api.fsbid.services.client as client_services

logger = logging.getLogger(__name__)


class AvailableBiddersListView(APIView):

    serializer_class = AvailableBiddersSerializer
    permission_classes = (IsAuthenticated, isDjangoGroupMember('cdo'),)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('ordering', openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Which field to use when ordering the results.')
        ])

    def get(self, request):
        '''
        Gets all available bidders for a CDO from FSBID
        '''
        return Response(client_services.get_available_bidders(request.META['HTTP_JWT'], True, request.query_params, f"{request.scheme}://{request.get_host()}"))

class AvailableBidderView(APIView):

    permission_classes = (IsAuthenticated, isDjangoGroupMember('cdo'),)
    serializer_class = AvailableBiddersSerializer

    def get(self, request, pk):
        """
        Return the user in Available Bidders list
        """
        return Response(AvailableBidders.objects.filter(bidder_perdet=pk))


class AvailableBiddersIdsListView(APIView):
    permission_classes = (IsAuthenticated, isDjangoGroupMember('cdo'),)


    def get(self, request, *args, **kwargs):
        """
        get:
        Return a list of the ids of the users in Available Bidders list
        """
        AvailableBidders.objects.values_list("bidder_perdet")
        return Response(AvailableBidders.objects.values_list("bidder_perdet", flat=True))


class AvailableBiddersActionView(FieldLimitableSerializerMixin,
                                       GenericViewSet,
                                       mixins.ListModelMixin,
                                       mixins.RetrieveModelMixin):
    '''
    add, remove, update an Available Bidder instance
    '''
    serializer_class = AvailableBiddersSerializer
    permission_classes = (IsAuthenticated, isDjangoGroupMember('cdo'),)

    def put(self, serializer, pk, **ars):
        '''
        Puts the client in the Available Bidders list
        '''
        user = UserProfile.objects.get(user=self.request.user)
        if AvailableBidders.objects.filter(bidder_perdet=pk).exists():
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            AvailableBidders.objects.create(last_editing_user=user, bidder_perdet=pk)
            return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, pk, format=None):
        '''
        Update's a client in the Available Bidders list
        '''
        bidder = get_object_or_404(AvailableBidders, bidder_perdet=pk)
        user = UserProfile.objects.get(user=self.request.user)
        serializer = self.serializer_class(bidder, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(last_editing_user=user, update_date=datetime.now())
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        '''
        Removes the client from the Available Bidders list
        '''
        AvailableBidders.objects.filter(bidder_perdet=pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AvailableBiddersCSVView(APIView):

    permission_classes = (IsAuthenticated, isDjangoGroupMember('cdo'),)

    def get(self, request, *args, **kwargs):
        """
        Return a list of all of the users in Available Bidders for CSV export
        """
        return services.get_available_bidders_csv(request)
