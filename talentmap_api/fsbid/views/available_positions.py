import logging
import coreapi
import math
import random

from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import status

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from talentmap_api.fsbid.filters import AvailablePositionsFilter
from talentmap_api.fsbid.views.base import BaseView

import talentmap_api.fsbid.services.available_positions as services

from talentmap_api.common.common_helpers import in_superuser_group

logger = logging.getLogger(__name__)


class FSBidAvailablePositionsListView(BaseView):

    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_class = AvailablePositionsFilter

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("ordering", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Ordering'),
            openapi.Parameter("page", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Page Index'),
            openapi.Parameter("limit", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Page Limit'),

            openapi.Parameter("cps_codes", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Handshake status (HS,OP)'),
            openapi.Parameter("id", openapi.IN_QUERY, type=openapi.TYPE_STRING, description="Available Position ids"),
            openapi.Parameter("is_available_in_bidcycle", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Bid Cycle id'),
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
            openapi.Parameter("htf_ind", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Hard to Fill (Y/N)'),
            openapi.Parameter("q", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Text search'),
        ])

    def get(self, request, *args, **kwargs):
        '''
        Gets all available positions
        '''
        return Response(services.get_available_positions(request.query_params, request.META['HTTP_JWT'], f"{request.scheme}://{request.get_host()}"))


class FSBidAvailablePositionsTandemListView(BaseView):

    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_class = AvailablePositionsFilter

    @swagger_auto_schema(
        manual_parameters=[
            # Pagination
            openapi.Parameter("ordering", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Ordering'),
            openapi.Parameter("page", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Page Index'),
            openapi.Parameter("limit", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Page Limit'),

            openapi.Parameter("getCount", openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN, description='Results Count'),

            # Tandem 1
            openapi.Parameter("cps_codes", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Handshake status (HS,OP)'),
            openapi.Parameter("id", openapi.IN_QUERY, type=openapi.TYPE_STRING, description="Available Position ids"),
            openapi.Parameter("is_available_in_bidcycle", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Bid Cycle id'),
            openapi.Parameter("language_codes", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Language code'),
            openapi.Parameter("position__bureau__code__in", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Bureau Code'),
            openapi.Parameter("position__grade__code__in", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Grade Code'),
            openapi.Parameter("position__position_number__in", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Position Numbers'),
            openapi.Parameter("position__post__tour_of_duty__code__in", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='TOD code - tandem'),
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
            openapi.Parameter("cps_codes-tandem", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Handshake status (HS,OP) - tandem'),
            openapi.Parameter("id-tandem", openapi.IN_QUERY, type=openapi.TYPE_STRING, description="Available Position ids - tandem"),
            openapi.Parameter("is_available_in_bidcycle-tandem", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Bid Cycle id - tandem'),
            openapi.Parameter("language_codes-tandem", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Language code - tandem'),
            openapi.Parameter("position__bureau__code__in-tandem", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Bureau Code - tandem'),
            openapi.Parameter("position__grade__code__in-tandem", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Grade Code - tandem'),
            openapi.Parameter("position__position_number__in-tandem", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Position Numbers'),
            openapi.Parameter("position__post__tour_of_duty__code__in-tandem", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='TOD code - tandem'),
            openapi.Parameter("position__skill__code__in-tandem", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Skill Code - tandem'),
        ])

    def get(self, request, *args, **kwargs):
        '''
        Gets all tandem available positions
        '''
        return Response(services.get_available_positions_tandem(request.query_params, request.META['HTTP_JWT'], f"{request.scheme}://{request.get_host()}"))


class FSBidAvailablePositionsCSVView(BaseView):

    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_class = AvailablePositionsFilter

    def get(self, request, *args, **kwargs):
        '''
        Gets all available positions
        '''
        includeLimit = True
        limit = 2000
        if in_superuser_group(request.user):
            limit = 9999999
            includeLimit = False
        return services.get_available_positions_csv(request.query_params, request.META['HTTP_JWT'], f"{request.scheme}://{request.get_host()}", limit, includeLimit)


class FSBidAvailablePositionsTandemCSVView(BaseView):

    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_class = AvailablePositionsFilter

    def get(self, request, *args, **kwargs):
        '''
        Gets all tandem available positions
        '''
        includeLimit = True
        limit = 2000
        if in_superuser_group(request.user):
            limit = 9999999
            includeLimit = False
        return services.get_available_positions_tandem_csv(request.query_params, request.META['HTTP_JWT'], f"{request.scheme}://{request.get_host()}", limit, includeLimit)


class FSBidAvailablePositionView(BaseView):

    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request, pk):
        '''
        Gets an available position
        '''
        result = services.get_available_position(pk, request.META['HTTP_JWT'])
        if result is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(result)


class FSBidUnavailablePositionView(BaseView):

    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request, pk):
        '''
        Gets an unavailable position
        '''
        result = services.get_unavailable_position(pk, request.META['HTTP_JWT'])
        if result is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(result)


class FSBidAvailablePositionsSimilarView(BaseView):

    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request, pk):
        '''
        Gets similar available positions to the position provided
        '''
        return Response(services.get_similar_available_positions(pk, request.META['HTTP_JWT']))


class FSBidAvailablePositionsFeaturedPositionsView(BaseView):

    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_class = AvailablePositionsFilter

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("limit", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Page Limit'),
            openapi.Parameter("position__grade__code__in", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Grade Code'),
            openapi.Parameter("position__post_indicator__in", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Use name values from /references/postindicators/'),
            openapi.Parameter("position__skill__code__in", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Skill Code'),
        ])

    def get(self, request, *args, **kwargs):
        '''
        Gets a random set of 3 featured positions
        '''

        count = services.get_available_positions_count(request.query_params, request.META['HTTP_JWT'], f"{request.scheme}://{request.get_host()}")["count"]

        if count is 0:
            return Response({})

        try:
            pageLimit = int(request.query_params["limit"])
            randomPage = random.randint(1, math.ceil(count / pageLimit)) #nosec
            newQueryParams = request.query_params.copy()
            newQueryParams["page"] = str(randomPage)
        except:
            return Response({})

        return Response(services.get_available_positions(newQueryParams, request.META['HTTP_JWT'], f"{request.scheme}://{request.get_host()}"))
