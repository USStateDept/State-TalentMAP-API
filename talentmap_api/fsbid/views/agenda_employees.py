import logging
from rest_framework.response import Response

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from talentmap_api.common.permissions import isDjangoGroupMember
from rest_condition import Or

from talentmap_api.fsbid.views.base import BaseView
import talentmap_api.fsbid.services.agenda_employees as services

logger = logging.getLogger(__name__)


class FSBidAgendaEmployeesListView(BaseView):
    
    permission_classes = [Or(isDjangoGroupMember('ao_user'), isDjangoGroupMember('cdo')), ]

    @swagger_auto_schema(
        manual_parameters=[
            # Pagination
            openapi.Parameter("ordering", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Ordering'),
            openapi.Parameter("page", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Page Index'),
            openapi.Parameter("limit", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Page Limit'),
            openapi.Parameter("q", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Free Text'),
        ])

    def get(self, request):
        '''
        Gets all agenda employees
        '''
        return Response(services.get_agenda_employees(request.query_params, request.META['HTTP_JWT'], f"{request.scheme}://{request.get_host()}"))
