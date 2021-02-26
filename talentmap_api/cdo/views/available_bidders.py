import logging
import coreapi
from django.shortcuts import get_object_or_404
from datetime import datetime

from rest_framework.schemas import AutoSchema
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

logger = logging.getLogger(__name__)


class AvailableBiddersListView(APIView):

    serializer_class = AvailableBiddersSerializer
    permission_classes = (IsAuthenticated, isDjangoGroupMember('cdo'),)

    schema = AutoSchema(
        manual_fields=[
            coreapi.Field("page", location='query', type='integer', description='A page number within the paginated result set.'),
            coreapi.Field("limit", location='query', type='integer', description='Number of results to return per page.'),
        ]
    )

    def get(self, request):
        """
        Return users in Available Bidders list
        """
        return Response(services.get_available_bidders(request.META['HTTP_JWT']))

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
        return services.get_available_bidders_csv(request.META['HTTP_JWT'])
