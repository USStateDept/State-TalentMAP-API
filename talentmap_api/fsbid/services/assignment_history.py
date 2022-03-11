import logging
# import pydash
# from copy import deepcopy
from urllib.parse import urlencode, quote
from django.conf import settings
import jwt

from talentmap_api.common.common_helpers import ensure_date
from talentmap_api.fsbid.services import common as services

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
    # this will need to be updated based on template columns we want
    query = {
        "ad_id": ad_id,
        "asgperdetseqnum": perdet_seq_num,
        # "asgposseqnum": asgposseqnum,
        # "asgdasgseqnum": asgdasgseqnum,
        # "asgdasgscode": asgdasgscode,
        # "asgdetadate": asgdetadate,
        # # "asgdetdteddate": asgdetdteddate,
        # "asgdtoddesctext": asgdtoddesctext,
        # "asgdcriticalneedind": asgdcriticalneedind,
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
    
    # need to update filters
    # asgdasgseqnum|EQ|274115|
    # asgdrevisionnum|EQ|4|
    # filters = [
        # { "key": "asgdasgseqnum", "comparator": "EQ", "value": query.get("asgdasgseqnum", None) },
        # { "key": "asgdrevisionnum", "comparator": "EQ", "value": query.get("asgdrevisionnum", None) },
    # ]
    # filters = pydash.filter_(filters, lambda o: o["value"] != None)
    # filters = pydash.map_(filters, lambda x: services.convert_to_fsbid_ql(x["key"], x["value"], x["comparator"], pydash.get(x, "isDate")))
    
    values = {
        "rp.pageNum": 10,
        # "rp.filter": filters,
    }
    return urlencode({i: j for i, j in values.items() if j is not None}, doseq=True, quote_via=quote)


def fsbid_assignment_history_to_tmap(assignments):
    # TO-DO:
    # mapping needs to be updated
    
    assignment_history = {
        "asgposseqnum": assignments["asgposseqnum"],
        "asgdasgseqnum": assignments["asgdasgseqnum"],
        "asgdrevisionnum": assignments["asgdrevisionnum"],
        "asgdasgscode": assignments["asgdasgscode"],
        "asgdetadate": ensure_date(assignments["asgdetadate"]),
        "asgdetdteddate": ensure_date(assignments["asgdetdteddate"]),
        "asgdtoddesctext": assignments["asgdtoddesctext"],
        "asgperdetseqnum": assignments["asgperdetseqnum"],
        "asgscode": "asgscode",
    }
    
    return assignment_history


def fsbid_assignments_to_talentmap_assignments(data):
    # hard_coded are the default data points (opinionated EP)
    # add_these are the additional data points we want returned

    hard_coded = [
        "asgposseqnum",
        "asgdasgseqnum",
        "asgdrevisionnum",
        "asgdasgscode",
        "asgdetadate",
        "asgdtoddesctext",
        "asgperdetseqnum",
        "asgscode",
        ]

    add_these = []

    cols_mapping = {
        "asg_seq_num": "asgseqnum",
        "asg_emp_seq_nbr": "asgempseqnbr",
        "asg_perdet_seqnum": "asgperdetseqnum",
        "asg_pos_seq_num": "asgposseqnum",
        "asg_create_id": "asgcreateid",
        "asg_create_date": "asgcreatedate",
        "asg_update_id": "asgupdateid",
        "asg_update_date": "asgupdatedate",
        "asgd_asg_seq_num": "asgdasgseqnum",
        "asgd_revision_num": "asgdrevisionnum",
        "asgd_asgs_code": "asgdasgscode",
        "asgd_lat_code": "asgdlatcode",
        "asgd_tfcd": "asgdtfcd",
        "asgd_tod_desc_text": "asgdtoddesctext",
        "asgd_tod_code": "asgdtodcode",
        "asgd_ail_seq_num": "asgdailseqnum",
        "asgd_org_code": "asgdorgcode",
        "asgd_wrt_code_rrrepay": "asgdwrtcoderrrepay",
        "asgd_tod_other_text": "asgdtodothertext",
        "asgd_tod_months_num": "asgdtodmonthsnum",
        "asgd_eta_date": "asgdetadate",
        "asgd_adjust_months_num": "asgdadjustmonthsnum",
        "asgd_etd_ted_date": "asgdetdteddate",
        "asgd_salary_reimburse_ind": "asgdsalaryreimburseind",
        "asgd_travelreimburse_ind": "asgdtravelreimburseind",
        "asgd_training_ind": "asgdtrainingind",
        "asgd_create_id": "asgdcreateid",
        "asgd_create_date": "asgdcreatedate",
        "asgd_update_id": "asgdupdateid",
        "asgd_update_date": "asgdupdatedate",
        "asgd_note_comment_text": "asgdnotecommenttext",
        "asgd_priority_ind": "asgdpriorityind",
        "asgd_critical_need_ind": "asgdcriticalneedind",
        "asgs_code": "asgscode",
        "asgs_desc_text": "asgsdesctext",
        "asgs_create_id": "asgscreateid",
        "asgs_create_date": "asgscreatedate",
        "asgs_update_id": "asgsupdateid",
        "asgs_update_date": "asgsupdatedate",
    }

    add_these.extend(hard_coded)

    return services.map_return_template_cols(add_these, cols_mapping, data)

