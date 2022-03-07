import logging
# from copy import deepcopy
from urllib.parse import urlencode, quote
from django.conf import settings
import jwt

from talentmap_api.common.common_helpers import ensure_date

ASSIGNMENTS_ROOT_V2 = settings.ASSIGNMENTS_API_V2_URL


logger = logging.getLogger(__name__)


def create_ai_assignment_history(jwt_token, perdet_seq_num, host=None):
    '''
    Get the assignment history for create agenda item reserach
    '''
    # TO-DO:
    # mapping needs to be updated
    from talentmap_api.fsbid.services.common import send_get_request
    from talentmap_api.fsbid.services.client import get_clients_count
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
        fsbid_assignment_history_to_tmap,
        get_clients_count,
        "/api/v1/assignments/",
        host,
        ASSIGNMENTS_ROOT_V2,
    )

    return response


# temporary, still working on mapping in other PR's
def assignment_history_temp(query):
    # TO-DO:
    # mapping needs to be updated
    values = {
        "rp.pageNum": 10,
        # "rp.filter": query.get("perdet_seq_num", None), asgperdetseqnum|EQ|6|
    }
    return urlencode({i: j for i, j in values.items() if j is not None}, doseq=True, quote_via=quote)


def fsbid_assignment_history_to_tmap(assignments):
    # TO-DO:
    # mapping needs to be updated
    assignmentsCopy = []
    assignment_history = []
    if type(assignments) is type(dict()):
        assignmentsCopy.append(assignments)
    else:
        assignmentsCopy = assignments

    if type(assignmentsCopy) is type([]):
        for x in assignmentsCopy:
            assignment_history.append(
                {
                    'asgposseqnum': x.get('asgposseqnum', None),
                    'asgdasgseqnum': x.get('asgdasgseqnum', None),
                    'asgdrevisionnum': x.get('asgdrevisionnum', None),
                    'asgdasgscode': x.get('asgdasgscode', None),
                    'asgdetadate': ensure_date(x.get('asgdetadate', None)),
                    'asgdetdteddate': ensure_date(x.get('asgdetdteddate', None)),
                    'asgdtoddesctext': x.get('asgdtoddesctext', None),
                    'asgperdetseqnum': x.get('asgperdetseqnum', None),
                    'asgscode': x.get('asgscode', None),
                }
            )
    return assignment_history