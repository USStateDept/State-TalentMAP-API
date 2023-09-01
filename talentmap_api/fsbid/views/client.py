import coreapi

from rest_framework.response import Response

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from talentmap_api.fsbid.views.base import BaseView
import talentmap_api.fsbid.services.client as services


class FSBidClientListView(BaseView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("hru_id", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='HRU id of the Agent'),
            openapi.Parameter("hru_id__in", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='HRU ids of the Agent (commma separated)'),
            openapi.Parameter("rl_cd", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Role code of the Agent'),
            openapi.Parameter("hasHandshake", openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN, description='True or False filter for clients with any offered handshakes'),
            openapi.Parameter("q", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Free Text'),
            openapi.Parameter("ordering", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Which field to use when ordering the results.'),
            openapi.Parameter("page", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='A page number within the paginated result set.'),
            openapi.Parameter("limit", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Number of results to return per page.'),
            openapi.Parameter("all_count", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Returns default value 99999 for front-end'),
        ])

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

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("hru_id", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='HRU id of the Agent'),
            openapi.Parameter("rl_cd", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Role code of the Agent'),
            openapi.Parameter("hasHandshake", openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN, description='True or False filter for clients with any offered handshakes')
        ])

    def get(self, request, *args, **kwargs):
        '''
        Exports all clients to CSV
        '''
        return services.get_client_csv(request.query_params, request.META['HTTP_JWT'], f"{request.scheme}://{request.get_host()}")
