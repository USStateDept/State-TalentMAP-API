from django.db.models import Count
from django.shortcuts import get_object_or_404

from rest_framework.viewsets import ReadOnlyModelViewSet, GenericViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import mixins

from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

from talentmap_api.common.mixins import FieldLimitableSerializerMixin, ActionDependentSerializerMixin
from talentmap_api.common.common_helpers import has_permission_or_403

from talentmap_api.position.models import Position, Classification, Assignment
from talentmap_api.position.filters import PositionFilter, AssignmentFilter
from talentmap_api.position.serializers import PositionSerializer, PositionWritableSerializer, ClassificationSerializer, AssignmentSerializer

from talentmap_api.user_profile.models import UserProfile


class PositionListView(FieldLimitableSerializerMixin,
                       ActionDependentSerializerMixin,
                       mixins.ListModelMixin,
                       mixins.RetrieveModelMixin,
                       mixins.UpdateModelMixin,
                       GenericViewSet):
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
        "partial_update": PositionWritableSerializer,
    }

    serializer_class = PositionSerializer
    filter_class = PositionFilter
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        queryset = Position.objects.all()
        queryset = self.serializer_class.prefetch_model(Position, queryset)
        return queryset


class PositionAssignmentHistoryView(FieldLimitableSerializerMixin,
                                    GenericViewSet,
                                    mixins.ListModelMixin):
    '''
    list:
    Lists all of the position's assignments
    '''

    serializer_class = AssignmentSerializer
    permission_classes = (IsAuthenticated,)
    filter_class = AssignmentFilter

    def get_queryset(self):
        # Get the position based on the PK from the url
        position = get_object_or_404(Position, pk=self.request.parser_context.get("kwargs").get("pk"))
        # Get the position's assignments
        queryset = position.assignments
        self.serializer_class.prefetch_model(Assignment, queryset)
        return queryset


class PositionFavoriteListView(FieldLimitableSerializerMixin,
                               ReadOnlyModelViewSet):
    """
    list:
    Return a list of all of the user's favorite positions.
    """

    serializer_class = PositionSerializer
    filter_class = PositionFilter
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = UserProfile.objects.get(user=self.request.user).favorite_positions.all()
        queryset = self.serializer_class.prefetch_model(Position, queryset)
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


class PositionFavoriteActionView(APIView):
    '''
    Controls the favorite status of a position

    Responses adapted from Github gist 'stars' https://developer.github.com/v3/gists/#star-a-gist
    '''

    permission_classes = (IsAuthenticated,)

    def get(self, request, pk, format=None):
        '''
        Indicates if the position is a favorite

        Returns 204 if the position is a favorite, otherwise, 404
        '''
        if UserProfile.objects.get(user=self.request.user).favorite_positions.filter(id=pk).exists():
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk, format=None):
        '''
        Marks the position as a favorite
        '''
        UserProfile.objects.get(user=self.request.user).favorite_positions.add(Position.objects.get(id=pk))
        return Response(status=status.HTTP_204_NO_CONTENT)

    def delete(self, request, pk, format=None):
        '''
        Removes the position from favorites
        '''
        UserProfile.objects.get(user=self.request.user).favorite_positions.remove(Position.objects.get(id=pk))
        return Response(status=status.HTTP_204_NO_CONTENT)


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
        has_permission_or_403(self.request.user, f"organization.can_highlight_positions_{position.bureau.code}")
        position.bureau.highlighted_positions.add(position)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def delete(self, request, pk, format=None):
        '''
        Removes the position from highlighted positions
        '''
        position = get_object_or_404(Position, id=pk)
        has_permission_or_403(self.request.user, f"organization.can_highlight_positions_{position.bureau.code}")
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
