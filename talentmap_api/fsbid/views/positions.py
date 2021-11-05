import logging
import coreapi

from rest_framework.permissions import IsAuthenticatedOrReadOnly

from rest_framework.response import Response
from rest_framework import status

from talentmap_api.fsbid.views.base import BaseView

import talentmap_api.fsbid.services.positions as services


logger = logging.getLogger(__name__)

    
class FSBidPositionView(BaseView):

    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request, pk):
        '''
        Gets generic position
        '''
        result = services.get_position(pk, request.META['HTTP_JWT'])
        if result is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(result)


