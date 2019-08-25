from dateutil.relativedelta import relativedelta

from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from django.utils import timezone

from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from talentmap_api.user_profile.models import UserProfile
from talentmap_api.common.permissions import isDjangoGroupMember

import talentmap_api.fsbid.services.bid as services

import logging
logger = logging.getLogger(__name__)


class FSBidListView(APIView):

    permission_classes = (IsAuthenticated, isDjangoGroupMember('bidder'),)

    @classmethod
    def get_extra_actions(cls):
        return []

    def get(self, request, *args, **kwargs):
        '''
        Gets all bids for the current user
        '''
        user = UserProfile.objects.get(user=self.request.user)
        return Response(services.user_bids(user.emp_id, 'JWTPLACEHOLDER'))


class FSBidListBidActionView(APIView):

    permission_classes = (IsAuthenticated, isDjangoGroupMember('bidder'),)

    def put(self, request, pk, format=None):
        '''
        Submits a bid (sets status to A)
        '''
        user = UserProfile.objects.get(user=self.request.user)
        try:
            services.bid_on_position(self.request.user.id, user.emp_id, pk, 'A', 'JWTPLACEHOLDER')
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_422_UNPROCESSABLE_ENTITY, data=e)


class FSBidListPositionActionView(APIView):
    '''
    list:
    Lists all bids for the user's current bidlist
    '''
    permission_classes = (IsAuthenticated, isDjangoGroupMember('bidder'),)

    def get(self, request, pk):
        '''
        Indicates if the position is in the user's bidlist

        Returns 204 if the position is in the list, otherwise, 404
        '''
        user = UserProfile.objects.get(user=self.request.user)
        if len(services.user_bids(user.emp_id, 'JWTPLACEHOLDER', pk)) > 0:
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk, format=None):
        '''
        Adds a cycle position to the user's bid list
        '''
        user = UserProfile.objects.get(user=self.request.user)
        services.bid_on_position(self.request.user.id, 'JWTPLACEHOLDER', user.emp_id, pk)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def delete(self, request, pk, format=None):
        '''
        Closes or deletes specified bid on a cycle position
        '''
        user = UserProfile.objects.get(user=self.request.user)
        services.remove_bid(user.emp_id, pk, 'JWTPLACEHOLDER')
        return Response(status=status.HTTP_204_NO_CONTENT)
