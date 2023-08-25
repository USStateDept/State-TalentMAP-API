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
        if result is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(result)
