import logging

from django.conf import settings

import talentmap_api.fsbid.services.employee as empservices
import talentmap_api.fsbid.services.bid as bidservices

from talentmap_api.available_positions.models import AvailablePositionRanking

logger = logging.getLogger(__name__)

API_ROOT = settings.FSBID_API_URL


def get_bidder_bids_and_rankings(self, request, pk):
    '''
    Return position information for all of bidders' bids including their ranking information for those positions
    '''
    # 1. grab user bidlist
    user_bids = bidservices.user_bids(pk, request.META['HTTP_JWT'])
    user_bids_filtered = []
    # 2. grab users' rankings
    user_rankings = AvailablePositionRanking.objects.filter(bidder_perdet=pk)
    for bid in user_bids:
        hasBureauPermissions = empservices.has_bureau_permissions(str(bid["position"]["id"]),self.request.META['HTTP_JWT'])
        hasOrgPermissions = empservices.has_org_permissions(str(bid["position"]["id"]), self.request.META['HTTP_JWT'])
        # 3. filter out based on bureau/org perms
        if hasOrgPermissions or hasBureauPermissions:
            # audit how much data is being sent to FE and how much we actually need
            bid["ranking"] = user_rankings.filter(cp_id=str(bid["position"]["id"])).values_list("rank", flat=True).first()
            user_bids_filtered.append(bid)

    # keep in mind that the ranking comes back as -1 the UI-Ranking
    return {
        "results": user_bids_filtered,
    }
