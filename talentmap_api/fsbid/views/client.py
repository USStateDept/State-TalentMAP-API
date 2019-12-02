from talentmap_api.fsbid.views.base import BaseView
import talentmap_api.fsbid.services.client as services
import talentmap_api.fsbid.services.common as common

from rest_framework.response import Response

from talentmap_api.fsbid.views.base import BaseView
from talentmap_api.common.permissions import isDjangoGroupMember
from rest_framework.permissions import IsAuthenticated
# do we have a cdo user permission? 

class FSBidCDOListView(BaseView):

    def get(self, request):
        '''
        Gets all cdos
        '''
        return Response(services.cdo(request.META['HTTP_JWT']))

class FSBidClientListView(BaseView):
    def get(self, hru_id, request):
        '''
        Get all clients by cdo_id/hru_id
        '''
        return Response(services.client(hru_id, request.META['HTTP_JWT']))