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

    hs = BidHandshake.objects.filter(cp_id=cp_id).values()
    
    active = pydash.find(hs, lambda x: x['status'] is not 'R')
    if active:
        props['active_handshake_perdet'] = active['bidder_perdet']

    return props
