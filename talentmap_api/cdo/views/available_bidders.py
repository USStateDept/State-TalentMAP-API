import logging
import coreapi
import pprint

from rest_framework.schemas import AutoSchema
from talentmap_api.cdo.serializers import AvailableBiddersSerializer
import talentmap_api.cdo.services.available_bidders as services
from talentmap_api.cdo.models import AvailableBidders
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated
from talentmap_api.user_profile.models import UserProfile

from talentmap_api.common.mixins import FieldLimitableSerializerMixin


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from talentmap_api.common.permissions import isDjangoGroupMember

logger = logging.getLogger(__name__)


class AvailableBiddersListView(APIView):

    permission_classes = (IsAuthenticated, isDjangoGroupMember('cdo'),)
    serializer_class = AvailableBiddersSerializer

    schema = AutoSchema(
        manual_fields=[
            coreapi.Field("page", location='query', type='integer', description='A page number within the paginated result set.'),
            coreapi.Field("limit", location='query', type='integer', description='Number of results to return per page.'),
            coreapi.Field("sort", location='query', type='string', description='a, b, or c'),
        ]
    )
    # will probably want a get_Bureau and a get_cdo for our toggling feature
    def get(self, request):
        """
        Return users in Available Bidders list
        """
        print('------------------ GET Available Bidders -------------')
        return Response(services.get_available_bidders(request.META['HTTP_JWT']))

class AvailableBidderView(APIView):

    permission_classes = (IsAuthenticated, isDjangoGroupMember('cdo'),)
    serializer_class = AvailableBiddersSerializer

    def get(self, request, pk):
        """
        Return the user in Available Bidders list
        """
        print('------------------ GET Available Bidder -------------')
        return Response(AvailableBidders.objects.filter(bidder_perdet=pk))


class AvailableBiddersIdsListView(APIView):
    permission_classes = (IsAuthenticated, isDjangoGroupMember('cdo'),)


    def get(self, request, *args, **kwargs):
        """
        get:
        Return a list of the ids of the users in Available Bidders list
        """
        print('------------------ GET Available Bidders\' IDs -------------')
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
        print('------------------ PUT Available Bidder -------------')
        user = UserProfile.objects.get(user=self.request.user)
        AvailableBidders.objects.create(last_editing_user_id=user, bidder_perdet=pk)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, pk, format=None):
        '''
        Update's a client in the Available Bidders list
        '''
        print('------------------ PATCH Available Bidder -------------')
        return Response(status=status.HTTP_204_NO_CONTENT)

    def delete(self, request, pk, format=None):
        '''
        Removes the client from the Available Bidders list
        '''
        print('------------------ DELETE Available Bidder -------------')
        AvailableBidders.objects.filter(bidder_perdet=pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AvailableBiddersCSVView(APIView):

    permission_classes = (IsAuthenticated, isDjangoGroupMember('cdo'),)

    def get(self, request, *args, **kwargs):
        """
        Return a list of all of the users in Available Bidders for CSV export
        """
        print('------------------hitting GET Available Bidders CSV -------------')
        return services.get_available_bidders_csv(AvailableBidders)
