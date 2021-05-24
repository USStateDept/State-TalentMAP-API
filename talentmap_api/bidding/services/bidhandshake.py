import logging
import pydash

from talentmap_api.bidding.models import BidHandshake

logger = logging.getLogger(__name__)


def get_position_handshake_data(cp_id):
    '''
    Return whether the cycle position is active and to which perdet, if any, possesses the active handshake
    '''
    props = {
        'active': False,
        'active_handshake_perdet': None,
    }

    hs = BidHandshake.objects.filter(cp_id=cp_id).values()
    active = pydash.filter_(hs, lambda x: x['status'] is not 'R')
    if len(active) is 0:
        props['active'] = True
    
    active = pydash.find(hs, lambda x: x['status'] is 'O' or x['status'] is 'A')
    if active:
        props['active_handshake_perdet'] = active['bidder_perdet']

    return props
