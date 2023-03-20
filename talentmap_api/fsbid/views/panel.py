import logging

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


from rest_framework.response import Response

from rest_condition import Or
from talentmap_api.common.permissions import isDjangoGroupMember


from talentmap_api.fsbid.views.base import BaseView

import talentmap_api.fsbid.services.panel as services

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

class PanelCategoriesView(BaseView):
    permission_classes = [Or(isDjangoGroupMember('cdo'), isDjangoGroupMember('ao_user'))]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("page", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='A page number within the paginated result set.'),
            openapi.Parameter("limit", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Number of results to return per page.'),
        ])

    def get(self, request, *args, **kwargs):
        '''
        Gets panel categories
        '''
        return Response(services.get_panel_categories(request.query_params, request.META['HTTP_JWT']))

class PanelDatesView(BaseView):
    permission_classes = [Or(isDjangoGroupMember('cdo'), isDjangoGroupMember('ao_user'))]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("page", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='A page number within the paginated result set.'),
            openapi.Parameter("limit", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Number of results to return per page.'),
        ])

    def get(self, request, *args, **kwargs):
        '''
        Gets panel dates
        '''
        return Response(services.get_panel_dates(request.query_params, request.META['HTTP_JWT']))

class PanelStatusesView(BaseView):
    permission_classes = [Or(isDjangoGroupMember('cdo'), isDjangoGroupMember('ao_user'))]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("page", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='A page number within the paginated result set.'),
            openapi.Parameter("limit", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Number of results to return per page.'),
        ])

    def get(self, request, *args, **kwargs):
        '''
        Gets panel statuses
        '''
        return Response(services.get_panel_statuses(request.query_params, request.META['HTTP_JWT']))

class PanelTypesView(BaseView):
    permission_classes = [Or(isDjangoGroupMember('cdo'), isDjangoGroupMember('ao_user'))]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("page", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='A page number within the paginated result set.'),
            openapi.Parameter("limit", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Number of results to return per page.'),
        ])

    def get(self, request, *args, **kwargs):
        '''
        Gets panel types
        '''
        return Response(services.get_panel_types(request.query_params, request.META['HTTP_JWT']))

class PanelMeetingsView(BaseView):
    # check perms assumptions
    permission_classes = [Or(isDjangoGroupMember('cdo'), isDjangoGroupMember('ao_user'))]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("page", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='A page number within the paginated result set.'),
            openapi.Parameter("limit", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Number of results to return per page.'),
            openapi.Parameter("ordering", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Sort Panel meetings'),
            openapi.Parameter("type", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Panel meeting type.'),
            openapi.Parameter("status", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Panel meeting status.'),
            openapi.Parameter("panel-date-start", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Panel meeting date start.'),
            openapi.Parameter("panel-date-end", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Panel meeting date end.'),
            openapi.Parameter("id", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Panel meeting seq num.'),
        ])

    def get(self, request, *args, **kwargs):
        '''
        Gets panel meetings
        '''
        return Response(services.get_panel_meetings(request.query_params, request.META['HTTP_JWT']))

class PanelMeetingsCSVView(BaseView):
    permission_classes = [Or(isDjangoGroupMember('ao_user'), isDjangoGroupMember('cdo')), ]

    @swagger_auto_schema(manual_parameters=base_parameters)

    def get(self, request):
        '''
        Exports all Panel Meetings to CSV format
        '''
        return services.get_panel_meetings_csv(request.query_params, request.META['HTTP_JWT'], f"{request.scheme}://{request.get_host()}")