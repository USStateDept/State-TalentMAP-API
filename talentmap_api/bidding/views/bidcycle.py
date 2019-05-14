from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from talentmap_api.common.common_helpers import in_group_or_403
from talentmap_api.common.permissions import isDjangoGroupMemberOrReadOnly
from talentmap_api.common.history_helpers import generate_historical_view
from talentmap_api.common.mixins import FieldLimitableSerializerMixin
from talentmap_api.position.serializers import PositionSerializer, Position, PositionDesignationSerializer
from talentmap_api.position.filters import PositionFilter

from talentmap_api.position.models import Position, PositionBidStatistics
from talentmap_api.bidding.models import BidCycle
from talentmap_api.bidding.filters import BidCycleFilter, PositionDesignationFilter
from talentmap_api.bidding.serializers.serializers import BidCycleSerializer, BidCycleStatisticsSerializer
from talentmap_api.user_profile.models import SavedSearch

import logging
logger = logging.getLogger(__name__)


HistoricalBidCycleView = generate_historical_view(BidCycle, BidCycleSerializer, BidCycleFilter)


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
    def get(self, request, format=None, **url_arguments):
        '''
        Indicates if the position is in the specified bid cycle

        Returns 204 if the position is in the cycle, otherwise, 404
        '''
        if get_object_or_404(BidCycle, id=url_arguments.get("pk")).positions.filter(id=url_arguments.get("pos_id")).count() > 0:
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def put(self, request, format=None, **url_arguments):
        '''
        Adds a position to the bid cycle
        '''
        in_group_or_403(self.request.user, 'bidcycle_admin')
        pid = url_arguments.get("pos_id")
        bidcycle = get_object_or_404(BidCycle, id=url_arguments.get("pk"))
        logger.info(f"User {self.request.user.id}:{self.request.user} adding position id {pid} to bidcycle {bidcycle}")
        bidcycle.positions.add(get_object_or_404(Position, id=pid))

        return Response(status=status.HTTP_204_NO_CONTENT)

    def delete(self, request, format=None, **url_arguments):
        '''
        Removes the position from the bid cycle
        '''
        in_group_or_403(self.request.user, 'bidcycle_admin')
        bidcycle = get_object_or_404(BidCycle, id=url_arguments.get("pk"))
        position = get_object_or_404(bidcycle.positions.all(), id=url_arguments.get("pos_id"))
        logger.info(f"User {self.request.user.id}:{self.request.user} removing position id {position.id} from bidcycle {bidcycle}")
        bidcycle.positions.remove(position)
        return Response(status=status.HTTP_204_NO_CONTENT)


class BidCycleBatchPositionActionView(APIView):
    def put(self, request, format=None, **url_arguments):
        '''
        Adds a batch of positions to the specified bidcycle using a saved search
        '''
        in_group_or_403(self.request.user, 'bidcycle_admin')
        search = get_object_or_404(SavedSearch, id=url_arguments.get("saved_search_id"))
        queryset = search.get_queryset()
        if not isinstance(queryset.first(), Position):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        bidcycle = get_object_or_404(BidCycle, id=url_arguments.get("pk"))
        logger.info(f"User {self.request.user.id}:{self.request.user} batch-adding saved search {search.id} to bidcycle {bidcycle}")
        bidcycle.positions.add(*list(queryset))
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
    permission_classes = (IsAuthenticatedOrReadOnly, isDjangoGroupMemberOrReadOnly('bidcycle_admin'))

    def get_queryset(self):
        queryset = BidCycle.objects.all()
        queryset = self.serializer_class.prefetch_model(BidCycle, queryset)
        return queryset


class BidCycleStatisticsView(mixins.ListModelMixin,
                             mixins.RetrieveModelMixin,
                             FieldLimitableSerializerMixin,
                             GenericViewSet):

    '''
    list:
    Returns a list of all bid cycles' statistics

    retrieve:
    Returns a specific bid cycle's statistics
    '''

    serializer_class = BidCycleStatisticsSerializer
    filter_class = BidCycleFilter
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        queryset = BidCycle.objects.all()
        queryset = self.serializer_class.prefetch_model(BidCycle, queryset)
        return queryset

class BidCyclePositionDesignationActionView(mixins.RetrieveModelMixin,
                                            mixins.UpdateModelMixin,
                                            FieldLimitableSerializerMixin,
                                            GenericViewSet):
    '''
    retrieve:
    Returns a specific bid cycle position designation

    partial_update:
    Updates a bid cycle's position designation
    '''
    serializer_class = PositionDesignationSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        position = get_object_or_404(Position, id=self.kwargs['pos_id'])
        bidcycle = get_object_or_404(BidCycle, id=self.kwargs['pk'])
        queryset = PositionBidStatistics.objects.filter(position=position, bidcycle=bidcycle)
        queryset = self.serializer_class.prefetch_model(PositionBidStatistics, queryset)
        return queryset

class BidCycleListPositionDesignationView(mixins.ListModelMixin,
                                          GenericViewSet):
    '''
    list:
    Returns all bid cycle position designations
    '''
    serializer_class = PositionDesignationSerializer
    filter_class = PositionDesignationFilter
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        bidcycle = get_object_or_404(BidCycle, id=self.kwargs['pk'])
        queryset = PositionBidStatistics.objects.filter(bidcycle=bidcycle)
        queryset = self.serializer_class.prefetch_model(PositionBidStatistics, queryset)
        return queryset