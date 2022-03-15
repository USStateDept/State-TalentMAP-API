import logging
import pydash
from urllib.parse import urlencode, quote
from django.conf import settings

from talentmap_api.common.common_helpers import ensure_date
from talentmap_api.fsbid.services import common as services

ASSIGNMENTS_ROOT_V2 = settings.ASSIGNMENTS_API_V2_URL


logger = logging.getLogger(__name__)


def create_ai_assignment_history(jwt_token, perdet_seq_num, host=None):
    '''
    Get the assignment history for create agenda item reserach
    '''
    query = {
        "asgperdetseqnum": perdet_seq_num,
    }
    response = services.send_get_request(
        "",
        query,
        assignment_history_temp,
        jwt_token,
        fsbid_assignments_to_talentmap_assignments,
        None,
        "/api/v2/assignments/",
        None,
        ASSIGNMENTS_ROOT_V2,
    )

    return response


# temporary, still working on mapping in other PR's
def assignment_history_temp(query):
    filters = [
        # mock needs to be updated for query/perdet
        # { "col": "asgperdetseqnum", "com": "EQ", "val": query.get("asgperdetseqnum", None) },
        { "col": "asgposseqnum", "com": "EQ", "val": 64327 },
    ]
    filters = pydash.filter_(filters, lambda o: o["val"] != None)
    filters = services.convert_to_fsbid_ql(filters)

    values = {
        "rp.pageNum": 1,
        "rp.filter": filters,
    }
    valuesToReturn = pydash.omit_by(values, lambda o: o is None or o == [])
    return urlencode(valuesToReturn, doseq=True, quote_via=quote)


def fsbid_assignments_to_talentmap_assignments(data):
    # hard_coded are the default data points (opinionated EP)
    # add_these are the additional data points we want returned

    hard_coded = [
        "asg_pos_seq_num",
        "asgd_asg_seq_num",
        "asgd_eta_date",
        "asgd_etd_ted_date",
        "asgd_tod_desc_text",
        "asg_perdet_seq_num",
        "asgs_code",
        "asgd_critical_need_ind",
        ]

    add_these = []

    cols_mapping = {
        "asg_seq_num": "asgseqnum",
        "asg_emp_seq_nbr": "asgempseqnbr",
        "asg_perdet_seq_num": "asgperdetseqnum",
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

