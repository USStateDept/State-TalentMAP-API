from talentmap_api.fsbid.views.base import BaseView
import talentmap_api.fsbid.services.client as services
import talentmap_api.fsbid.services.common as common

from talentmap_api.common.permissions import isDjangoGroupMember
# do we have a cdo user permission? 

# base view vs api view???
Class FSBidAgentView(baseview)
    permission_classes = (IsAuthenticated, isDjangoGroupMember('cdo'),)

    def get(self, request, pk)
        '''
        Get All CDOs (agents)
        '''
        return Response(services.agents(request.query_params.get('CDO', None), request.META['HTTP_JWT']))