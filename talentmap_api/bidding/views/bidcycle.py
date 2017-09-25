from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import status

from talentmap_api.common.mixins import FieldLimitableSerializerMixin
from talentmap_api.position.serializers import PositionSerializer
from talentmap_api.position.filters import PositionFilter

from talentmap_api.position.models import Position
from talentmap_api.bidding.models import BidCycle
from talentmap_api.bidding.filters import BidCycleFilter
from talentmap_api.bidding.serializers import BidCycleSerializer


class BidCycleListPositionView(mixins.ListModelMixin,
                               GenericViewSet):
    '''
    list:
    Lists all positions in the specified bid cycle
    '''
    serializer_class = PositionSerializer
    filter_class = PositionFilter

    def get_queryset(self):
        pk = self.kwargs.get("pk")
        queryset = BidCycle.objects.get(id=pk).positions
        queryset = self.serializer_class.prefetch_model(Position, queryset)
        return queryset


class BidCyclePositionActionView(APIView):
    def get(self, request, pk, pos_id, format=None):
        '''
        Indicates if the position is in the specified bid cycle

        Returns 204 if the position is in the cycle, otherwise, 404
        '''
        if BidCycle.objects.get(id=pk).positions.filter(id=pos_id).count() > 0:
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk, pos_id, format=None):
        '''
        Adds a position to the bid cycle
        '''
        BidCycle.objects.get(id=pk).positions.add(Position.objects.get(id=pos_id))
        return Response(status=status.HTTP_204_NO_CONTENT)

    def delete(self, request, pk, pos_id, format=None):
        '''
        Removes the position from the bid cycle
        '''
        position = Position.objects.get(id=pos_id)
        BidCycle.objects.get(id=pk).positions.remove(position)
        return Response(status=status.HTTP_204_NO_CONTENT)


class BidCycleView(mixins.ListModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.CreateModelMixin,
                   mixins.UpdateModelMixin,
                   FieldLimitableSerializerMixin,
                   GenericViewSet):

    '''
    list:
    Returns a list of all bid cycles

    retrieve:
    Returns a specific bid cycle

    create:
    Creates a new bid cycle

    partial_update:
    Updates a bid cycle's parameters
    '''

    serializer_class = BidCycleSerializer
    filter_class = BidCycleFilter
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        queryset = BidCycle.objects.all()
        queryset = self.serializer_class.prefetch_model(BidCycle, queryset)
        return queryset
