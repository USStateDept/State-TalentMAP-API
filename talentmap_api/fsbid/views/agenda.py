import coreapi

from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_condition import Or

from talentmap_api.fsbid.views.base import BaseView
import talentmap_api.fsbid.services.agenda as services
from talentmap_api.common.permissions import isDjangoGroupMember

import logging
logger = logging.getLogger(__name__)


class AgendaItemView(BaseView):
    permission_classes = [Or(isDjangoGroupMember('cdo'), isDjangoGroupMember('bureau'), isDjangoGroupMember('ao'),)]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("perdet", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Perdet of the employee'),
            openapi.Parameter("ordering", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Which field to use when ordering the results.'),
            openapi.Parameter("page", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='A page number within the paginated result set.'),
            openapi.Parameter("limit", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Number of results to return per page.'),
        ])

    def get(self, request):
        '''
        Gets all Agenda Items for a CDO/AO
        '''
        return Response(services.get_agenda_items(request.META['HTTP_JWT'], request.query_params, f"{request.scheme}://{request.get_host()}"))


class AgendaItemCSVView(BaseView):
    permission_classes = [Or(isDjangoGroupMember('cdo'), isDjangoGroupMember('bureau'), isDjangoGroupMember('ao'),)]

    def get(self, request):
        """
        Return a list of all of the items in Agenda Item History for CSV export
        """
        return services.get_agenda_item_history_csv(request.query_params, request.META['HTTP_JWT'], f"{request.scheme}://{request.get_host()}")

