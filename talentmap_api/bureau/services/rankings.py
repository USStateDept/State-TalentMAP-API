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
    # 2. grab users' rankings
    user_rankings = AvailablePositionRanking.objects.filter(bidder_perdet=pk)
    # 3. filter out bids not on shortlist
    shortlist_bids = list(filter(lambda x: (user_rankings.filter(cp_id=str(x["position"]["id"])).exists()), user_bids))
    filtered_bids = []
    for bid in shortlist_bids:
        pos_id = str(bid["position"]["id"])
        hasBureauPermissions = empservices.has_bureau_permissions(pos_id,self.request.META['HTTP_JWT'])
        hasOrgPermissions = empservices.has_org_permissions(pos_id, self.request.META['HTTP_JWT'])
        # 4. filter out based on bureau/org perms
        if hasOrgPermissions or hasBureauPermissions:
            # audit how much data is being sent to FE and how much we actually need
            bid["ranking"] = user_rankings.filter(cp_id=pos_id).values_list("rank", flat=True).first()
            filtered_bids.append(bid)

    # keep in mind that the ranking comes back as -1 the UI-Ranking
    return {
        "results": filtered_bids,
    }
