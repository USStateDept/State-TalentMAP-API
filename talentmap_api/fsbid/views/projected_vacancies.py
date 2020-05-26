import coreapi

from dateutil.relativedelta import relativedelta

from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from django.utils import timezone

from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.schemas import AutoSchema

from rest_framework.response import Response
from rest_framework import status

from talentmap_api.user_profile.models import UserProfile
from talentmap_api.fsbid.filters import ProjectedVacancyFilter

from talentmap_api.fsbid.views.base import BaseView
import talentmap_api.fsbid.services.projected_vacancies as services

from talentmap_api.common.common_helpers import in_superuser_group

import logging
logger = logging.getLogger(__name__)


class FSBidProjectedVacanciesListView(BaseView):

    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_class = ProjectedVacancyFilter
    schema = AutoSchema(
        manual_fields=[
            # Pagination
            coreapi.Field("ordering", location='query', description='Ordering'),
            coreapi.Field("page", location='query', description='Page Index'),
            coreapi.Field("limit", location='query', description='Page Limit'),

            coreapi.Field("id", location="query", description="Projected Vacancies ids"),
            coreapi.Field("is_available_in_bidseason", location='query', description='Bid Season id'),
            coreapi.Field("is_domestic", location='query', description='Is the position domestic? (true/false)'),
            coreapi.Field("language_codes", location='query', description='Language code'),
            coreapi.Field("position__bureau__code__in", location='query', description='Bureau Code'),
            coreapi.Field("position__grade__code__in", location='query', description='Grade Code'),
            coreapi.Field("position__position_number__in", location='query', description='Position Numbers'),
            coreapi.Field("position__post__code__in", location='query', description='Post id'),
            coreapi.Field("position__post__danger_pay__in", location='query', description='Danger pay'),
            coreapi.Field("position__post__differential_rate__in", location='query', description='Diff. Rate'),
            coreapi.Field("position__post_indicator__in", location='query', description='Use name values from /references/postindicators/'),
            coreapi.Field("position__post__tour_of_duty__code__in", location='query', description='TOD code'),
            coreapi.Field("position__skill__code__in", location='query', description='Skill Code'),
            coreapi.Field("position__us_codes__in", location='query', description='Use code values from /references/unaccompaniedstatuses/'),
            coreapi.Field("q", location='query', description='Free Text'),
        ]
    )

    def get(self, request, *args, **kwargs):
        '''
        Gets all projected vacancies
        '''
        return Response(services.get_projected_vacancies(request.query_params, request.META['HTTP_JWT'], f"{request.scheme}://{request.get_host()}"))

class FSBidProjectedVacanciesTandemListView(BaseView):

    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_class = ProjectedVacancyFilter
    schema = AutoSchema(
        manual_fields=[
            # Pagination
            coreapi.Field("ordering", location='query', description='Ordering'),
            coreapi.Field("page", location='query', description='Page Index'),
            coreapi.Field("limit", location='query', description='Page Limit'),

            coreapi.Field("getCount", location='query', description='Results Count'),

            # Tandem 1
            coreapi.Field("id", location="query", description="Projected Vacancies ids"),
            coreapi.Field("is_available_in_bidseason", location='query', description='Bid Season id'),
            coreapi.Field("language_codes", location='query', description='Language code'),
            coreapi.Field("position__bureau__code__in", location='query', description='Bureau Code'),
            coreapi.Field("position__grade__code__in", location='query', description='Grade Code'),
            coreapi.Field("position__position_number__in", location='query', description='Position Numbers'),
            coreapi.Field("position__post__tour_of_duty__code__in", location='query', description='TOD code'),
            coreapi.Field("position__skill__code__in", location='query', description='Skill Code'),

            # Common
            coreapi.Field("is_domestic", location='query', description='Is the position domestic? (true/false)'),
            coreapi.Field("position__post__code__in", location='query', description='Post id'),
            coreapi.Field("position__post__danger_pay__in", location='query', description='Danger pay'),
            coreapi.Field("position__post__differential_rate__in", location='query', description='Diff. Rate'),
            coreapi.Field("position__post_indicator__in", location='query', description='Use name values from /references/postindicators/'),
            coreapi.Field("position__us_codes__in", location='query', description='Use code values from /references/unaccompaniedstatuses/'),
            coreapi.Field("q", location='query', description='Text search'),

            # Tandem 2
            # Exclude post, post differentials, is_domestic
            coreapi.Field("id-tandem", location="query", description="Available Position ids - tandem"),
            coreapi.Field("is_available_in_bidseason-tandem", location='query', description='Bid Season id - tandem'),
            coreapi.Field("language_codes-tandem", location='query', description='Language code - tandem'),
            coreapi.Field("position__bureau__code__in-tandem", location='query', description='Bureau Code - tandem'),
            coreapi.Field("position__grade__code__in-tandem", location='query', description='Grade Code - tandem'),
            coreapi.Field("position__position_number__in-tandem", location='query', description='Position Numbers'),
            coreapi.Field("position__post__tour_of_duty__code__in-tandem", location='query', description='TOD code - tandem'),
            coreapi.Field("position__skill__code__in-tandem", location='query', description='Skill Code - tandem'),
        ]
    )

    def get(self, request, *args, **kwargs):
        '''
        Gets all tandem projected vacancies
        '''
        return Response(services.get_projected_vacancies_tandem(request.query_params, request.META['HTTP_JWT'], f"{request.scheme}://{request.get_host()}"))

class FSBidProjectedVacancyView(BaseView):

    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request, pk):
        '''
        Gets a projected vacancy
        '''
        result = services.get_projected_vacancy(pk, request.META['HTTP_JWT'])
        if result is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(result)

class FSBidProjectedVacanciesCSVView(BaseView):

    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_class = ProjectedVacancyFilter

    def get(self, request, *args, **kwargs):
        includeLimit = True
        limit = 2000
        if in_superuser_group(request.user):
            limit = 9999999
            includeLimit = False
        return services.get_projected_vacancies_csv(request.query_params, request.META['HTTP_JWT'], f"{request.scheme}://{request.get_host()}", limit, includeLimit)

class FSBidProjectedVacanciesTandemCSVView(BaseView):

    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_class = ProjectedVacancyFilter

    def get(self, request, *args, **kwargs):
        includeLimit = True
        limit = 2000
        if in_superuser_group(request.user):
            limit = 9999999
            includeLimit = False
        return services.get_projected_vacancies_tandem_csv(request.query_params, request.META['HTTP_JWT'], f"{request.scheme}://{request.get_host()}", limit, includeLimit)
