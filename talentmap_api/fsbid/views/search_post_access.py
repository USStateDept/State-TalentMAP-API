from talentmap_api.fsbid.views.base import BaseView
from rest_framework.response import Response
from rest_framework import status
import talentmap_api.fsbid.services.search_post_access as services

class FSBidSearchPostAccessViewFilters(BaseView):
    '''
    Gets the Filters for the Search Post Access Page
    '''

    def get(self, request):
        jwt = request.META['HTTP_JWT']
        result = services.get_search_post_access_filters(jwt, request.query_params)
        return Response(result)

class FSBidSearchPostAccessActionView(BaseView):
    '''
    Gets the Data for the Search Post Access Page
    '''
    def post(self, request):
        jwt = request.META['HTTP_JWT']
        result = services.get_search_post_access_data(jwt, request.data)
        return Response(result)

class FSBidSearchPostAccessRemoveActionView(BaseView):
    '''
    Gets the Data for the Search Post Access Page
    '''
    def post(self, request):
        jwt = request.META['HTTP_JWT']
        result = services.remove_search_post_access(jwt, request.data)
        return Response(result)
