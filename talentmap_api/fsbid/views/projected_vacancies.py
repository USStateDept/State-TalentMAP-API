import logging
import coreapi

from rest_framework.permissions import IsAuthenticatedOrReadOnly

from rest_framework.response import Response
from rest_framework import status

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from talentmap_api.fsbid.filters import ProjectedVacancyFilter

from talentmap_api.fsbid.views.base import BaseView
import talentmap_api.fsbid.services.projected_vacancies as services

from talentmap_api.common.common_helpers import in_superuser_group

logger = logging.getLogger(__name__)


class FSBidProjectedVacanciesListView(BaseView):

    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_class = ProjectedVacancyFilter

    @swagger_auto_schema(
        manual_parameters=[
            # Pagination
            openapi.Parameter("ordering", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Ordering'),
            openapi.Parameter("page", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Page Index'),
            openapi.Parameter("limit", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Page Limit'),

            openapi.Parameter("id", openapi.IN_QUERY, type=openapi.TYPE_STRING, description="Projected Vacancies ids"),
            openapi.Parameter("is_available_in_bidseason", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Bid Season id'),
            openapi.Parameter("is_domestic", openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN, description='Is the position domestic? (true/false)'),
            openapi.Parameter("language_codes", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Language code'),
            openapi.Parameter("position__bureau__code__in", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Bureau Code'),
            openapi.Parameter("position__grade__code__in", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Grade Code'),
            openapi.Parameter("position__position_number__in", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Position Numbers'),
            openapi.Parameter("position__post__code__in", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Post id'),
            openapi.Parameter("position__post__danger_pay__in", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Danger pay'),
            openapi.Parameter("position__post__differential_rate__in", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Diff. Rate'),
            openapi.Parameter("position__post_indicator__in", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Use name values from /references/postindicators/'),
            openapi.Parameter("position__post__tour_of_duty__code__in", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='TOD code'),
            openapi.Parameter("position__skill__code__in", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Skill Code'),
            openapi.Parameter("position__us_codes__in", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Use code values from /references/unaccompaniedstatuses/'),
            openapi.Parameter("q", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Free Text'),
        ])

    def get(self, request, *args, **kwargs):
        '''
        Gets all projected vacancies
        '''
        return Response(services.get_projected_vacancies(request.query_params, request.META['HTTP_JWT'], f"{request.scheme}://{request.get_host()}"))


class FSBidProjectedVacanciesTandemListView(BaseView):

    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_class = ProjectedVacancyFilter

    @swagger_auto_schema(
        manual_parameters=[
            # Pagination
            openapi.Parameter("ordering", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Ordering'),
            openapi.Parameter("page", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Page Index'),
            openapi.Parameter("limit", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Page Limit'),

            openapi.Parameter("getCount", openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN, description='Results Count'),

            # Tandem 1
            openapi.Parameter("id", openapi.IN_QUERY, type=openapi.TYPE_STRING, description="Projected Vacancies ids"),
            openapi.Parameter("is_available_in_bidseason", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Bid Season id'),
            openapi.Parameter("language_codes", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Language code'),
            openapi.Parameter("position__bureau__code__in", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Bureau Code'),
            openapi.Parameter("position__grade__code__in", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Grade Code'),
            openapi.Parameter("position__position_number__in", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Position Numbers'),
            openapi.Parameter("position__post__tour_of_duty__code__in", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='TOD code'),
            openapi.Parameter("position__skill__code__in", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Skill Code'),

            # Common
            openapi.Parameter("is_domestic", openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN, description='Is the position domestic? (true/false)'),
            openapi.Parameter("position__post__code__in", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Post id'),
            openapi.Parameter("position__post__danger_pay__in", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Danger pay'),
            openapi.Parameter("position__post__differential_rate__in", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Diff. Rate'),
            openapi.Parameter("position__post_indicator__in", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Use name values from /references/postindicators/'),
            openapi.Parameter("position__us_codes__in", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Use code values from /references/unaccompaniedstatuses/'),
            openapi.Parameter("position__cpn_codes__in", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Use code values from /references/commuterposts/'),
            openapi.Parameter("q", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Text search'),

            # Tandem 2
            # Exclude post, post differentials, is_domestic
            openapi.Parameter("id-tandem", openapi.IN_QUERY, type=openapi.TYPE_STRING, description="Available Position ids - tandem"),
            openapi.Parameter("is_available_in_bidseason-tandem", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Bid Season id - tandem'),
            openapi.Parameter("language_codes-tandem", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Language code - tandem'),
            openapi.Parameter("position__bureau__code__in-tandem", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Bureau Code - tandem'),
            openapi.Parameter("position__grade__code__in-tandem", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Grade Code - tandem'),
            openapi.Parameter("position__position_number__in-tandem", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Position Numbers'),
            openapi.Parameter("position__post__tour_of_duty__code__in-tandem", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='TOD code - tandem'),
            openapi.Parameter("position__skill__code__in-tandem", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Skill Code - tandem'),
        ])

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
