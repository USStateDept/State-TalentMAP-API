import logging

from talentmap_api.fsbid.views.base import BaseView
from rest_framework.response import Response
from rest_framework import status
import talentmap_api.fsbid.services.search_post_access as services

logger = logging.getLogger(__name__)

class FSBidPostAccessFiltersView(BaseView):
    '''
    Gets the Filters for the Search Post Access Page
    '''
    def get(self, request):
        jwt = request.META['HTTP_JWT']
        result = services.get_post_access_filters(jwt)
        return Response(result)

class FSBidPostAccessListView(BaseView):
    '''
    Gets the Data for the Search Post Access Page
    '''
    def get(self, request):
        jwt = request.META['HTTP_JWT']
        result = services.get_post_access_data(jwt, request.query_params)
        return Response(result)

class FSBidPostAccessActionView(BaseView):
    '''
    Gets the Data for the Search Post Access Page
    '''
    def delete(self, request):
        jwt = request.META['HTTP_JWT']
        print(request)
        result = services.remove_post_access_permissions(jwt, request.data)
        return Response(result)
