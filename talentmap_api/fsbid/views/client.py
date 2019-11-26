from talentmap_api.fsbid.views.base import BaseView
import talentmap_api.fsbid.services.client as services
import talentmap_api.fsbid.services.common as common

from talentmap_api.fsbid.views.base import BaseView
from talentmap_api.common.permissions import isDjangoGroupMember
from rest_framework.permissions import IsAuthenticated
# do we have a cdo user permission? 

# base view vs api view???
class FSBidCDOListView(BaseView):
    uri = "agents"
    mapping_function = services.fsbid_cdo_list_to_talentmap_cdo_list