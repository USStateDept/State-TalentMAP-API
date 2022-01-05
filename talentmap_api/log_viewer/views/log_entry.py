import coreapi
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from talentmap_api.common.permissions import isDjangoGroupMember
import talentmap_api.log_viewer.services as services
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class LogEntryListView(APIView):
    permission_classes = (IsAuthenticated, isDjangoGroupMember('superuser'))

    @classmethod
    def get_extra_actions(cls):
        return []

    def get(self, request, *args, **kwargs):
        '''
        Lists all logs
        '''
        return Response(services.get_log_list())


class LogEntryView(APIView):
    permission_classes = (IsAuthenticated, isDjangoGroupMember('superuser'))

    @classmethod
    def get_extra_actions(cls):
        return []

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('size', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Last x number of lines to retrieve from the log file.')
        ])

    def get(self, request, *args, **kwargs):
        '''
        Shows specific log
        '''
        log_name = self.request.parser_context.get("kwargs").get("string")
        size = request.query_params.get('size', 10000)
        resp = services.get_log(log_name, size)
        if resp:
            return Response(resp)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
