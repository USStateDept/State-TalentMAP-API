from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from talentmap_api.common.permissions import isDjangoGroupMember
from talentmap_api.log_viewer.models import LogEntry
import talentmap_api.log_viewer.services as services
from rest_framework.response import Response
from rest_framework import status


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

    def get(self, request, *args, **kwargs):
        '''
        Shows specific log
        '''
        log_name = self.request.parser_context.get("kwargs").get("string")
        resp = services.get_log(log_name)
        if resp:
            return Response(services.get_log(log_name))
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
