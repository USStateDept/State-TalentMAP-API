import logging
# from copy import deepcopy
# from urllib.parse import urlencode, quote
from django.conf import settings
import jwt

from talentmap_api.fsbid.requests import requests

# CLIENTS_ROOT_V2 = settings.CLIENTS_API_V2_URL
ASSIGNMENT_HISTORY_ROOT_V2 = settings.ASSIGNMENT_HISTORY_API_V2_URL


logger = logging.getLogger(__name__)


def create_ai_assignment_history(jwt_token, perdet_seq_num, host=None):
    '''
    Get the assignment history for create agenda item reserach
    '''
    print('------------create ai assign hist service test------------')
    print('perdert', perdet_seq_num)
    print('------------create ai assign hist service test------------')
    from talentmap_api.fsbid.services.common import send_get_request
    from talentmap_api.fsbid.services.client import fsbid_assignments_to_tmap, convert_client_query
    ad_id = jwt.decode(jwt_token, verify=False).get('unique_name')
    query = {
        "ad_id": ad_id,
        "perdet_seq_num": perdet_seq_num,
        "currentAssignmentOnly": "false",
    }
    response = send_get_request(
        "",
        query,
        convert_client_query,
        jwt_token,
        fsbid_assignments_to_tmap,
        "/api/v1/assignments/",
        host,
        # CLIENTS_ROOT_V2,
        ASSIGNMENT_HISTORY_ROOT_V2,
    )

    return response