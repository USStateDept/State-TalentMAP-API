from dateutil.relativedelta import relativedelta

from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from django.utils import timezone

from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from talentmap_api.user_profile.models import UserProfile
from talentmap_api.fsbid.filters import AvailablePositionsFilter

import talentmap_api.fsbid.services.available_positions as services

import logging
logger = logging.getLogger(__name__)

class BaseView(APIView):
    @classmethod
    def get_extra_actions(cls):
        return []

class FSBidAvailablePositionsListView(BaseView):

    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_class = AvailablePositionsFilter

    def get(self, request, *args, **kwargs):
        '''
        Gets all available positions
        '''
        return Response(services.get_available_positions(request.query_params, request.META['HTTP_JWT'], f"{request.scheme}://{request.get_host()}"))


class FSBidAvailablePositionView(BaseView):
    
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request, pk):
        '''
        Gets an available position
        '''
        return Response(services.get_available_position(pk, request.META['HTTP_JWT']))


class FSBidAvailablePositionsSimilarView(BaseView):
    
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request, pk):
        '''
        Gets similar available positions to the position provided
        '''
        return Response(services.get_similar_available_positions(pk, request.META['HTTP_JWT']))
