import coreapi

from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_condition import Or

from talentmap_api.fsbid.views.base import BaseView
import talentmap_api.fsbid.services.agenda as services
from talentmap_api.common.permissions import isDjangoGroupMember

import logging
logger = logging.getLogger(__name__)


class AgendaItemView(BaseView):
    permission_classes = [Or(isDjangoGroupMember('cdo'), isDjangoGroupMember('ao_user'),)]

    def get(self, request, pk):
        '''
        Get single agenda by ai_seq_num
        '''
        return Response(services.get_single_agenda_item(request.META['HTTP_JWT'], pk))
    

class AgendaItemListView(BaseView):
    permission_classes = [Or(isDjangoGroupMember('cdo'), isDjangoGroupMember('ao_user'),)]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("perdet", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Perdet of the employee'),
            openapi.Parameter("ordering", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Which field to use when ordering the results.'),
            openapi.Parameter("page", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='A page number within the paginated result set.'),
            openapi.Parameter("limit", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Number of results to return per page.'),
        ])

    def get(self, request):
        '''
        Gets all Agenda Items
        '''
        return Response(services.get_agenda_items(request.META['HTTP_JWT'], request.query_params, f"{request.scheme}://{request.get_host()}"))


class AgendaItemActionView(BaseView):
    permission_classes = [Or(isDjangoGroupMember('cdo'), isDjangoGroupMember('ao_user'),)]

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'assignmentId': openapi.Schema(type=openapi.TYPE_STRING, description='Assignment ID'),
            'assignmentVersion': openapi.Schema(type=openapi.TYPE_STRING, description='Assignment Version'),
            'personId': openapi.Schema(type=openapi.TYPE_INTEGER, description='Person ID'),
            'personDetailId': openapi.Schema(type=openapi.TYPE_INTEGER, description='Person Detail ID'),
            'agendaStatusCode': openapi.Schema(type=openapi.TYPE_STRING, description='Agenda Status Code'),
            'panelMeetingId': openapi.Schema(type=openapi.TYPE_INTEGER, description='Panel Meeting ID'),
            'panelMeetingCategory': openapi.Schema(type=openapi.TYPE_STRING, description='Panel Meeting Category'),
            'agendaLegs': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(
                type=openapi.TYPE_OBJECT,
                properties={
                    'legAssignmentId': openapi.Schema(type=openapi.TYPE_STRING, description='Leg Assignment ID'),
                    'legAssignmentVersion': openapi.Schema(type=openapi.TYPE_STRING, description='Leg Assignment Version'),
                    'legActionType': openapi.Schema(type=openapi.TYPE_STRING, description='Leg Action Type'),
                    'tourOfDutyCode': openapi.Schema(type=openapi.TYPE_STRING, description='Tour Of Duty Code'),
                    'legStartDate': openapi.Schema(type=openapi.TYPE_STRING, description='Leg Start Date'),
                    'legEndDate': openapi.Schema(type=openapi.TYPE_STRING, description='Leg End Date'),
                    'travelFunctionCode': openapi.Schema(type=openapi.TYPE_STRING, description='Travel Function Code'),
                    'posSeqNum': openapi.Schema(type=openapi.TYPE_INTEGER, description='Position ID'),
                    'cpId': openapi.Schema(type=openapi.TYPE_STRING, description='Cycle Position ID'),
                 }), description='Legs'),
    }))

    def post(self, request):
        '''
        Create single agenda
        '''
        try:
            services.create_agenda(request.data, request.META['HTTP_JWT'])
            return Response(status=status.HTTP_204_NO_CONTENT)    
        except Exception as e:
            logger.info(f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}. User {self.request.user}")
            return Response(status=status.HTTP_422_UNPROCESSABLE_ENTITY)


class AgendaItemCSVView(BaseView):
    permission_classes = [Or(isDjangoGroupMember('cdo'), isDjangoGroupMember('ao_user'),)]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("perdet", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Perdet of the Employee.'),
            openapi.Parameter("ordering", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Which field to use when ordering the results.'),
        ])

    def get(self, request):
        """
        Return a list of Agenda Items for CSV export
        """
        return services.get_agenda_item_history_csv(request.query_params, request.META['HTTP_JWT'], f"{request.scheme}://{request.get_host()}")

class AgendaRemarksView(BaseView):
    permission_classes = [Or(isDjangoGroupMember('cdo'), isDjangoGroupMember('ao_user'))]

    def get(self, request):
        """
        Return a list of reference data for all remarks
        """
        return Response(services.get_agenda_remarks(request.query_params, request.META['HTTP_JWT']))

class AgendaRemarkCategoriesView(BaseView):
    permission_classes = [Or(isDjangoGroupMember('cdo'), isDjangoGroupMember('ao_user'))]

    def get(self, request):
        """
        Return a list of reference data for all remark categories
        """
        return Response(services.get_agenda_remark_categories(request.query_params, request.META['HTTP_JWT']))

class AgendaStatusesView(BaseView):
    permission_classes = [Or(isDjangoGroupMember('cdo'), isDjangoGroupMember('ao_user'))]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("page", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='A page number within the paginated result set.'),
            openapi.Parameter("limit", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Number of results to return per page.'),
        ])

    def get(self, request):
        """
        Return a list of reference data for all agenda statuses
        """
        return Response(services.get_agenda_statuses(request.query_params, request.META['HTTP_JWT']))

class AgendaLegActionTypesView(BaseView):
    permission_classes = [Or(isDjangoGroupMember('cdo'), isDjangoGroupMember('ao_user'))]

    def get(self, request):
        """
        Return a list of reference data for all agenda leg-action-types
        """
        return Response(services.get_agenda_leg_action_types(request.query_params, request.META['HTTP_JWT']))

class PanelAgendasListView(BaseView):
    permission_classes = [Or(isDjangoGroupMember('cdo'), isDjangoGroupMember('ao_user'),)]

    def get(self, request, pk):
        '''
        Get agendas for a panel meeting
        '''
        return Response(services.get_agendas_by_panel(pk, request.META['HTTP_JWT']))
