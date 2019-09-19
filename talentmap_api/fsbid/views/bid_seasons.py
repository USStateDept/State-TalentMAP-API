from dateutil.relativedelta import relativedelta

from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from django.utils import timezone

from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

from rest_framework.response import Response
from rest_framework import status

from talentmap_api.user_profile.models import UserProfile

from talentmap_api.fsbid.views.base import BaseView
import talentmap_api.fsbid.services.bid_season as services

import logging
logger = logging.getLogger(__name__)


class FSBidBidSeasonsListView(BaseView):

    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request, *args, **kwargs):
        '''
        Gets all bid seasons
        '''
        return Response(services.get_bid_seasons(request.query_params.get('bsn_future_vacancy_ind', None), request.META['HTTP_JWT']))
