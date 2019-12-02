from talentmap_api.fsbid.views.base import BaseView
import talentmap_api.fsbid.services.client as services
import talentmap_api.fsbid.services.common as common

from rest_framework.response import Response

from talentmap_api.fsbid.views.base import BaseView
from talentmap_api.common.permissions import isDjangoGroupMember
from rest_framework.permissions import IsAuthenticated

class FSBidClientListView(BaseView):

    def get(self, request):
        '''
        Gets all cdos
        '''
        return Response(services.cdo(request.META['HTTP_JWT']))