import logging
import pydash

from talentmap_api.bidding.models import BidHandshake

logger = logging.getLogger(__name__)


def get_position_handshake_data(cp_id):
    '''
    Return whether the cycle position is active, and if so, to which perdet possesses the active handshake
    '''
    props = {
        'active_handshake_perdet': None,
    }

    perdet = BidHandshake.objects.filter(cp_id=cp_id).exclude(status='R').values_list("bidder_perdet", flat=True)
    
    if perdet:
        props['active_handshake_perdet'] = perdet.first()

    return props
