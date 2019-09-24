from django.shortcuts import render
from django.http import QueryDict

from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from talentmap_api.common.mixins import FieldLimitableSerializerMixin
from talentmap_api.available_positions.models import AvailablePositionFavorite

from talentmap_api.user_profile.models import UserProfile

import talentmap_api.fsbid.services.available_positions as services


class AvailablePositionFavoriteListView(APIView):

    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        """
        get:
        Return a list of all of the user's favorite available positions.
        """
        user = UserProfile.objects.get(user=self.request.user)
        aps = AvailablePositionFavorite.objects.filter(user=user).values_list("cp_id", flat=True)
        if len(aps) > 0:
            pos_nums = ','.join(aps)
            return Response(services.get_available_positions(QueryDict(f"id={pos_nums}"), request.META['HTTP_JWT']))
        else:
            return Response({"count": 0, "next": None, "previous": None, "results": []})


class AvailablePositionFavoriteActionView(APIView):
    '''
    Controls the favorite status of a available position

    Responses adapted from Github gist 'stars' https://developer.github.com/v3/gists/#star-a-gist
    '''

    permission_classes = (IsAuthenticated,)

    def get(self, request, pk, format=None):
        '''
        Indicates if the available position is a favorite

        Returns 204 if the available position is a favorite, otherwise, 404
        '''
        user = UserProfile.objects.get(user=self.request.user)
        if AvailablePositionFavorite.objects.filter(user=user, cp_id=pk).exists():
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk, format=None):
        '''
        Marks the available position as a favorite
        '''
        user = UserProfile.objects.get(user=self.request.user)
        AvailablePositionFavorite.objects.get_or_create(user=user, cp_id=pk)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def delete(self, request, pk, format=None):
        '''
        Removes the available position from favorites
        '''
        user = UserProfile.objects.get(user=self.request.user)
        AvailablePositionFavorite.objects.filter(user=user, cp_id=pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
