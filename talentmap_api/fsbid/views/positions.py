import logging
import coreapi

from rest_framework.permissions import IsAuthenticatedOrReadOnly

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_condition import Or

from rest_framework.response import Response
from rest_framework import status

from talentmap_api.fsbid.views.base import BaseView

import talentmap_api.fsbid.services.positions as services


logger = logging.getLogger(__name__)

    
class FSBidPositionView(BaseView):

    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request, pk):
        '''
        Gets generic position
        '''
        result = services.get_position(pk, request.META['HTTP_JWT'])
        if result is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(result)

class FSBidPositionListView(BaseView):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("id", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='pos_seq_num of position.'),
            openapi.Parameter("page", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='A page number within the paginated result set.'),
            openapi.Parameter("limit", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Number of results to return per page.'),
            openapi.Parameter("ordering", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Number of results to return per page.'),
            openapi.Parameter("position_num", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Position number.'),
        ])

    def get(self, request):
        '''
        Gets generic positions
        '''
        result = services.get_positions(request.query_params, request.META['HTTP_JWT'])
        if result is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(result)


