import logging
import pydash
from rest_framework.response import Response

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from talentmap_api.common.permissions import isDjangoGroupMember
from rest_condition import Or

from talentmap_api.fsbid.views.base import BaseView
import talentmap_api.fsbid.services.agenda_employees as services

logger = logging.getLogger(__name__)


base_parameters = [
    # Pagination
    openapi.Parameter("ordering", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Ordering'),
    openapi.Parameter("q", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Free Text'),
    openapi.Parameter("current-bureaus", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Current bureaus, comma separated'),
    openapi.Parameter("handshake-bureaus", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Handshake bureaus, comma separated'),
    openapi.Parameter("current-organizations", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Current organizations, comma separated'),
    openapi.Parameter("handshake-organizations", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Handshake organizations, comma separated'),
    openapi.Parameter("ted-start", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='TED start date'),
    openapi.Parameter("ted-end", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='TED end date'),
    openapi.Parameter("cdo", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='CDO codes, comma separated'),
    openapi.Parameter("handshake", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Handshake codes, comma separated (Y, N)'),
]

class FSBidAgendaEmployeesListView(BaseView):
    
    permission_classes = [Or(isDjangoGroupMember('ao_user'), isDjangoGroupMember('cdo')), ]

    @swagger_auto_schema(
        manual_parameters=pydash.concat([
            openapi.Parameter("limit", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Page Limit'),
        ],
        base_parameters)
    )

    def get(self, request):
        '''
        Gets all agenda employees
        '''
        return Response(services.get_agenda_employees(request.query_params, request.META['HTTP_JWT'], f"{request.scheme}://{request.get_host()}"))


class FSBidAgendaEmployeesCSVView(BaseView):
    
    permission_classes = [Or(isDjangoGroupMember('ao_user'), isDjangoGroupMember('cdo')), ]

    @swagger_auto_schema(manual_parameters=base_parameters)

    def get(self, request):
        '''
        Gets all agenda employees
        '''
        return services.get_agenda_employees_csv(request.query_params, request.META['HTTP_JWT'], f"{request.scheme}://{request.get_host()}")


class FSBidPersonCurrentOrganizationsView(BaseView):
    uri = "v1/tm-persons/reference/current-organizations?rp.pageRows=0&rp.pageNum=0"
    mapping_function = services.fsbid_person_current_organization_to_talentmap


class FSBidPersonHandshakeOrganizationsView(BaseView):
    uri = "v1/tm-persons/reference/handshake-organizations?rp.pageRows=0&rp.pageNum=0"
    mapping_function = services.fsbid_person_handshake_organization_to_talentmap

class FSBidPersonCurrentBureausView(BaseView):
    uri = "v1/tm-persons/reference/current-bureaus?rp.pageRows=0&rp.pageNum=0"
    mapping_function = services.fsbid_person_current_bureau_to_talentmap


class FSBidPersonHandshakeBureausView(BaseView):
    uri = "v1/tm-persons/reference/handshake-bureaus?rp.pageRows=0&rp.pageNum=0"
    mapping_function = services.fsbid_person_handshake_bureau_to_talentmap