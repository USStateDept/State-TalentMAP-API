from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from talentmap_api.common.permissions import isDjangoGroupMember
from talentmap_api.fsbid.views.base import BaseView
from rest_condition import Or
import logging
import talentmap_api.fsbid.services.publishable_positions as services


logger = logging.getLogger(__name__)

class FSBidCapsuleActionView(APIView):

    permission_classes = (IsAuthenticated, isDjangoGroupMember('bureau_user'),)
    
    def get(self, request, pk):
        '''
        Get single capsule description
        '''
        result = services.get_capsule_description(pk, request.META['HTTP_JWT'])
        if result is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(result)

    def patch(self, request, pk):
        '''
        Updates a capsule description
        '''
        try:
            services.update_capsule_description(pk, request.META['HTTP_JWT'])
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.error(f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}. User {self.request.user}")
            return Response(status=status.HTTP_422_UNPROCESSABLE_ENTITY)


