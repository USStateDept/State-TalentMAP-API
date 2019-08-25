from django.db.models import Count
from django.shortcuts import get_object_or_404

from rest_framework.viewsets import ReadOnlyModelViewSet, GenericViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import mixins

from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

from talentmap_api.common.cache.views import CachedViewSet
from talentmap_api.common.mixins import FieldLimitableSerializerMixin, ActionDependentSerializerMixin
from talentmap_api.common.common_helpers import has_permission_or_403, in_group_or_403
from talentmap_api.common.permissions import isDjangoGroupMember

from talentmap_api.bidding.models import Bid, CyclePosition
from talentmap_api.bidding.serializers.serializers import BidSerializer, WaiverSerializer, CyclePositionSerializer, CyclePositionListSerializer
from talentmap_api.bidding.filters import BidFilter, WaiverFilter, CyclePositionFilter

from talentmap_api.user_profile.models import UserProfile


class CyclePositionListView(FieldLimitableSerializerMixin,
                            ActionDependentSerializerMixin,
                            CachedViewSet):
    """
    retrieve:
    Return the given cycle position.

    list:
    Return a list of all positions.

    """

    serializers = {
        "default": CyclePositionSerializer,
        "list": CyclePositionListSerializer,
    }

    serializer_class = CyclePositionSerializer
    filter_class = CyclePositionFilter
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        queryset = CyclePosition.objects.filter(bidcycle__active=True, status_code__in=["HS", "OP"], posted_date__isnull=False)
        queryset = self.serializer_class.prefetch_model(CyclePosition, queryset)
        return queryset


class CyclePositionBidListView(FieldLimitableSerializerMixin,
                          mixins.ListModelMixin,
                          GenericViewSet):
    """
    list:
    Return a list of all of the cycle position's bids.
    """

    serializer_class = BidSerializer
    filter_class = BidFilter
    permission_classes = (IsAuthenticated, isDjangoGroupMember('bureau_ao'))

    def get_queryset(self):
        # Get the position based on the PK from the url
        cp = get_object_or_404(CyclePosition, position_id=self.request.parser_context.get("kwargs").get("pk"))
        position = cp.position
        in_group_or_403(self.request.user, f"bureau_ao:{position.bureau.code}")
        # Get the position's bids
        queryset = cp.bids
        self.serializer_class.prefetch_model(Bid, queryset)
        return queryset


class CyclePositionSimilarView(FieldLimitableSerializerMixin,
                          mixins.ListModelMixin,
                          GenericViewSet):
    """
    list:
    Return a list of similar cycle positions to the specified position.
    """

    serializer_class = CyclePositionSerializer
    filter_class = CyclePositionFilter
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        # Get the position based on the PK from the url
        position = get_object_or_404(CyclePosition, pk=self.request.parser_context.get("kwargs").get("pk"))
        # Get the position's similar positions
        queryset = position.similar_positions
        self.serializer_class.prefetch_model(CyclePosition, queryset)
        return queryset

class CyclePositionHighlightListView(FieldLimitableSerializerMixin,
                                ReadOnlyModelViewSet):
    """
    list:
    Return a list of all currently highlighted positions
    """

    serializer_class = CyclePositionSerializer
    filter_class = CyclePositionFilter

    def get_queryset(self):
        queryset = CyclePosition.objects.annotate(highlight_count=Count('position__highlighted_by_org')).filter(highlight_count__gt=0, bidcycle__active=True, status_code__in=["HS", "OP"])
        queryset = self.serializer_class.prefetch_model(CyclePosition, queryset)
        return queryset

class CyclePositionFavoriteListView(FieldLimitableSerializerMixin,
                                    ReadOnlyModelViewSet):
    """
    list:
    Return a list of all of the user's favorite cycle positions.
    """

    serializer_class = CyclePositionSerializer
    filter_class = CyclePositionFilter
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = UserProfile.objects.get(user=self.request.user).favorite_positions.all()
        queryset = self.serializer_class.prefetch_model(CyclePosition, queryset)
        return queryset

class CyclePositionFavoriteActionView(APIView):
    '''
    Controls the favorite status of a cycle position

    Responses adapted from Github gist 'stars' https://developer.github.com/v3/gists/#star-a-gist
    '''

    permission_classes = (IsAuthenticated,)

    def get(self, request, pk, format=None):
        '''
        Indicates if the cycle position is a favorite

        Returns 204 if the cycle position is a favorite, otherwise, 404
        '''
        if UserProfile.objects.get(user=self.request.user).favorite_positions.filter(id=pk).exists():
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk, format=None):
        '''
        Marks the cycle position as a favorite
        '''
        UserProfile.objects.get(user=self.request.user).favorite_positions.add(CyclePosition.objects.get(id=pk))
        return Response(status=status.HTTP_204_NO_CONTENT)

    def delete(self, request, pk, format=None):
        '''
        Removes the cycle position from favorites
        '''
        UserProfile.objects.get(user=self.request.user).favorite_positions.remove(CyclePosition.objects.get(id=pk))
        return Response(status=status.HTTP_204_NO_CONTENT)
