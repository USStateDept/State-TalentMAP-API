import coreapi

from talentmap_api.fsbid.views.base import BaseView
import talentmap_api.fsbid.services.client as services
import talentmap_api.fsbid.services.common as common

from rest_framework.response import Response
from rest_framework.schemas import AutoSchema

from talentmap_api.fsbid.views.base import BaseView
from talentmap_api.common.permissions import isDjangoGroupMember
from rest_framework.permissions import IsAuthenticated

import talentmap_api.fsbid.services.client as services


class FSBidClientListView(BaseView):
    schema = AutoSchema(
        manual_fields=[
            coreapi.Field("hru_id", location='query', description='HRU id of the Agent'),
            coreapi.Field("rl_cd", location='query', description='Role code of the Agent'),
            coreapi.Field("hasHandshake", location='query', description='Clients handshake status')
        ]
    )
    def get(self, request):
        '''
        Gets all clients for a CDO
        '''
        return Response(services.client(request.META['HTTP_JWT'], request.query_params.get('hru_id'), request.query_params.get('rl_cd'), request.query_params.get('hasHandshake')))


class FSBidClientView(BaseView):

    def get(self, request, pk):
        '''
        Gets a single client by perdet_seq_num
        '''
        return Response(services.single_client(request.META['HTTP_JWT'], pk))

class FSBidClientSuggestionsView(BaseView):

    def get(self, request, pk):
        '''
        Gets suggestions for a single client by perdet_seq_num
        '''
        return Response(services.client_suggestions(request.META['HTTP_JWT'], pk))

class FSBidClientCSVView(BaseView):

    schema = AutoSchema(
        manual_fields=[
            coreapi.Field("hru_id", location='query', description='HRU id of the Agent'),
            coreapi.Field("rl_cd", location='query', description='Role code of the Agent'),
            coreapi.Field("hs_cd", location='query', description='Handshake filter')
        ]
    )

    def get(self, request, *args, **kwargs):
        '''
        Exports all clients to CSV
        '''
        return services.get_client_csv(request.query_params, request.META['HTTP_JWT'], f"{request.scheme}://{request.get_host()}")
