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
from talentmap_api.fsbid.filters import ProjectedVacancyFilter

import talentmap_api.fsbid.services as services

import logging
logger = logging.getLogger(__name__)

class FSBidProjectedVacanciesListView(APIView):

    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_class = ProjectedVacancyFilter

    @classmethod
    def get_extra_actions(cls):
        return []

    def get(self, request, *args, **kwargs):
        '''
        Gets all projected vacancies
        '''
        return Response(services.get_projected_vacancies(request.query_params, f"{request.scheme}://{request.get_host()}"))