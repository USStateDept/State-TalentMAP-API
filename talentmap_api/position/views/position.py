from django.db.models import Count
from django.shortcuts import get_object_or_404

from rest_framework.viewsets import ReadOnlyModelViewSet, GenericViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import mixins

from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

from talentmap_api.common.cache.views import CachedViewSet
from talentmap_api.common.history_helpers import generate_historical_view
from talentmap_api.common.mixins import FieldLimitableSerializerMixin, ActionDependentSerializerMixin
from talentmap_api.common.common_helpers import has_permission_or_403, in_group_or_403
from talentmap_api.common.permissions import isDjangoGroupMember

from talentmap_api.bidding.models import Bid, Waiver, CyclePosition
from talentmap_api.bidding.serializers.serializers import BidSerializer, WaiverSerializer, CyclePositionSerializer
from talentmap_api.bidding.filters import BidFilter, WaiverFilter

from talentmap_api.position.models import Position, Classification, Assignment
from talentmap_api.position.filters import PositionFilter, AssignmentFilter
from talentmap_api.position.serializers import PositionSerializer, PositionListSerializer, PositionWritableSerializer, ClassificationSerializer, AssignmentSerializer

from talentmap_api.user_profile.models import UserProfile


HistoricalPositionView = generate_historical_view(Position, PositionSerializer, PositionFilter)


class PositionListView(FieldLimitableSerializerMixin,
                       ActionDependentSerializerMixin,
                       mixins.UpdateModelMixin,
                       CachedViewSet):
    """
    retrieve:
    Return the given position.

    list:
    Return a list of all positions.

    partial_update:
    Update a position
    """

    serializers = {
        "default": PositionSerializer,
        "list": PositionListSerializer,
        "partial_update": PositionWritableSerializer,
    }

    serializer_class = PositionSerializer
    filter_class = PositionFilter
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):	   
        position_ids = CyclePosition.objects.filter(bidcycle__active=True, status_code__in=["HS", "OP"]).values_list("position_id", flat=True)
        queryset = Position.objects.filter(id__in=position_ids)
        queryset = self.serializer_class.prefetch_model(Position, queryset)	
        return queryset


class PositionWaiverListView(FieldLimitableSerializerMixin,
                             mixins.ListModelMixin,
                             GenericViewSet):
    """
    list:
    Return a list of all of the position's waivers.
    """

    serializer_class = WaiverSerializer
    filter_class = WaiverFilter
    permission_classes = (IsAuthenticated, isDjangoGroupMember('bureau_ao'))

    def get_queryset(self):
        # Get the position based on the PK from the url
        position = get_object_or_404(Position, pk=self.request.parser_context.get("kwargs").get("pk"))
        in_group_or_403(self.request.user, f"bureau_ao:{position.bureau.code}")
        # Get the position's bids
        queryset = position.waivers
        self.serializer_class.prefetch_model(Waiver, queryset)
        return queryset


class PositionSimilarView(FieldLimitableSerializerMixin,
                          mixins.ListModelMixin,
                          GenericViewSet):
    """
    list:
    Return a list of similar positions to the specified position.
    """

    serializer_class = PositionSerializer
    filter_class = PositionFilter
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        # Get the position based on the PK from the url
        position = get_object_or_404(Position, pk=self.request.parser_context.get("kwargs").get("pk"))
        # Get the position's similar positions
        queryset = position.similar_positions
        self.serializer_class.prefetch_model(Position, queryset)
        return queryset


class PositionWaiverActionView(GenericViewSet):
    '''
    Controls the status of a waiver
    '''

    permission_classes = (IsAuthenticated, isDjangoGroupMember('bureau_ao'))

    def get_waiver(self, user, position_pk, waiver_pk):
        position = get_object_or_404(Position, pk=position_pk)
        in_group_or_403(user, f"bureau_ao:{position.bureau.code}")
        return get_object_or_404(position.waivers, pk=waiver_pk)

    def approve(self, request, format=None, **url_kwargs):
        '''
        Approves the specified waiver request

        Returns 204 if the operation is successful
        '''
        # Get the position based on the PK from the url
        waiver = self.get_waiver(self.request.user, position_pk=url_kwargs.get('pk'), waiver_pk=url_kwargs.get('waiver_pk'))
        waiver.status = waiver.Status.approved
        waiver.reviewer = self.request.user.profile
        waiver.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    def deny(self, request, format=None, **url_kwargs):
        '''
        Denies the specified waiver request

        Returns 204 if the operation is successful
        '''
        # Get the position based on the PK from the url
        waiver = self.get_waiver(self.request.user, position_pk=url_kwargs.get('pk'), waiver_pk=url_kwargs.get('waiver_pk'))
        waiver.status = waiver.Status.denied
        waiver.reviewer = self.request.user.profile
        waiver.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


class PositionAssignmentHistoryView(FieldLimitableSerializerMixin,
                                    GenericViewSet,
                                    mixins.ListModelMixin):
    '''
    list:
    Lists all of the position's assignments
    '''

    serializer_class = AssignmentSerializer
    permission_classes = (IsAuthenticated, isDjangoGroupMember('bureau_ao'))
    filter_class = AssignmentFilter

    def get_queryset(self):
        # Get the position based on the PK from the url
        position = get_object_or_404(Position, pk=self.request.parser_context.get("kwargs").get("pk"))
        # Get the position's assignments
        queryset = position.assignments
        self.serializer_class.prefetch_model(Assignment, queryset)
        return queryset

class PositionHighlightListView(FieldLimitableSerializerMixin,
                                ReadOnlyModelViewSet):
    """
    list:
    Return a list of all currently highlighted positions
    """

    serializer_class = PositionSerializer
    filter_class = PositionFilter

    def get_queryset(self):
        queryset = Position.objects.annotate(highlight_count=Count('highlighted_by_org')).filter(highlight_count__gt=0)
        queryset = self.serializer_class.prefetch_model(Position, queryset)
        return queryset

class PositionHighlightActionView(APIView):
    '''
    Controls the highlighted status of a position

    Responses adapted from Github gist 'stars' https://developer.github.com/v3/gists/#star-a-gist
    '''

    permission_classes = (IsAuthenticated,)

    def get(self, request, pk, format=None):
        '''
        Indicates if the position is highlighted

        Returns 204 if the position is highlighted, otherwise, 404
        '''
        position = get_object_or_404(Position, id=pk)
        if position.highlighted_by_org.count() > 0:
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk, format=None):
        '''
        Marks the position as highlighted by the position's bureau
        '''
        position = get_object_or_404(Position, id=pk)

        # Check for the bureau permission on the accessing user
        in_group_or_403(self.request.user, "superuser")
        position.bureau.highlighted_positions.add(position)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def delete(self, request, pk, format=None):
        '''
        Removes the position from highlighted positions
        '''
        position = get_object_or_404(Position, id=pk)
        in_group_or_403(self.request.user, "superuser")
        position.bureau.highlighted_positions.remove(position)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ClassificationListView(FieldLimitableSerializerMixin,
                             ReadOnlyModelViewSet):
    """
    retrieve:
    Return the given classification.

    list:
    Return a list of all position classifications.
    """

    serializer_class = ClassificationSerializer

    def get_queryset(self):
        queryset = Classification.objects.all()
        queryset = self.serializer_class.prefetch_model(Classification, queryset)
        return queryset
