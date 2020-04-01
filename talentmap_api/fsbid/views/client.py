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
            coreapi.Field("hru_id__in", location='query', description='HRU ids of the Agent (commma separated)'),
            coreapi.Field("rl_cd", location='query', description='Role code of the Agent'),
            coreapi.Field("hasHandshake", location='query', description='True or False filter for clients with any offered handshakes'),
            coreapi.Field("q", location='query', description='Free Text'),
            coreapi.Field("ordering", location='query', description='Which field to use when ordering the results.'),
            coreapi.Field("page", location='query', type='integer', description='A page number within the paginated result set.'),
            coreapi.Field("limit", location='query', type='integer', description='Number of results to return per page.'),
            coreapi.Field("all_count", location='query', type='integer', description='Returns default value 99999 for front-end'),
        ]
    )
    def get(self, request):
        '''
        Gets all clients for a CDO
        '''
        return Response(services.client(request.META['HTTP_JWT'], request.query_params, f"{request.scheme}://{request.get_host()}"))

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
            coreapi.Field("hasHandshake", location='query', description='True or False filter for clients with any offered handshakes')
        ]
    )

    def get(self, request, *args, **kwargs):
        '''
        Exports all clients to CSV
        '''
        return services.get_client_csv(request.query_params, request.META['HTTP_JWT'], f"{request.scheme}://{request.get_host()}")
