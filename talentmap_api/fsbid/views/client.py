import coreapi

from talentmap_api.fsbid.views.base import BaseView
import talentmap_api.fsbid.services.client as services
import talentmap_api.fsbid.services.common as common

from rest_framework.response import Response
from rest_framework.schemas import AutoSchema

from talentmap_api.fsbid.views.base import BaseView
from talentmap_api.common.permissions import isDjangoGroupMember
from rest_framework.permissions import IsAuthenticated


class FSBidClientListView(BaseView):
    schema = AutoSchema(
        manual_fields=[
            coreapi.Field("hru_id", location='query', description='HRU id of the Agent'),
            coreapi.Field("rl_cd", location='query', description='Role code of the Agent')
        ]
    )
    def get(self, request):
        '''
        Gets all clients for the currently logged in user
        '''
        return Response(services.client(request.META['HTTP_JWT'], request.query_params.get('hru_id')))


class FSBidClientView(BaseView):
    
    def get(self, request, pk):
        '''
        Gets a single client by perdet_seq_num
        '''
        return Response(services.single_client(request.META['HTTP_JWT'], pk))