import coreapi

from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_condition import Or

from talentmap_api.fsbid.views.base import BaseView
from talentmap_api.fsbid.services.assignment_history import get_assignments, assignment_history_to_client_format
from talentmap_api.common.permissions import isDjangoGroupMember

import logging
logger = logging.getLogger(__name__)


class FSBidAssignmentHistoryListView(BaseView):
    permission_classes = [Or(isDjangoGroupMember('cdo'), isDjangoGroupMember('ao_user'),)]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("page", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='A page number within the paginated result set.'),
            openapi.Parameter('limit', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Number of results to return per page.')
        ])

    def get(self, request, pk):
        '''
        Gets a single client's assignment history
        '''
        query_copy = request.query_params.copy()
        query_copy["perdet_seq_num"] = pk 
        query_copy._mutable = False
        data = assignment_history_to_client_format(get_assignments(query_copy, request.META['HTTP_JWT']))
        return Response(data)
