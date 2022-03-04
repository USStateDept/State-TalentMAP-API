import logging
# from copy import deepcopy
from urllib.parse import urlencode, quote
from django.conf import settings
import jwt

from talentmap_api.fsbid.requests import requests

# CLIENTS_ROOT_V2 = settings.CLIENTS_API_V2_URL
ASSIGNMENTS_ROOT_V2 = settings.ASSIGNMENTS_API_V2_URL


logger = logging.getLogger(__name__)


def create_ai_assignment_history(jwt_token, perdet_seq_num, host=None):
    '''
    Get the assignment history for create agenda item reserach
    '''
    print('------------create ai assign hist service test------------')
    print('perdert', perdet_seq_num)
    print('------------create ai assign hist service test------------')
    # TO-DO:
    # mapping for statuses needs to be updated
    from talentmap_api.fsbid.services.common import send_get_request
    from talentmap_api.fsbid.services.client import fsbid_assignments_to_tmap, get_clients_count
    ad_id = jwt.decode(jwt_token, verify=False).get('unique_name')
    query = {
        "ad_id": ad_id,
        "perdet_seq_num": perdet_seq_num,
        "currentAssignmentOnly": "false",
        "rp.pageNum": 1, 
    }
    response = send_get_request(
        "",
        query,
        assignment_history_temp,
        jwt_token,
        fsbid_assignments_to_tmap,
        get_clients_count,
        "/api/v1/assignments/",
        host,
        # CLIENTS_ROOT_V2,
        ASSIGNMENTS_ROOT_V2,
    )

    return response


# temporary, still working on mapping in other PR's
def assignment_history_temp(query):
    '''
    Needs to be updated
    '''
    values = {
        "rp.pageNum": 10,
        # "rp.filter": query.get("perdet_seq_num", None), asgperdetseqnum|EQ|6|
    }
    return urlencode({i: j for i, j in values.items() if j is not None}, doseq=True, quote_via=quote)
