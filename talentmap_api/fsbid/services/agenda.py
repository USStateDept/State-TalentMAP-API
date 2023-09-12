import csv
import logging
from functools import partial
from urllib.parse import urlencode, quote
from datetime import datetime
import jwt
import pydash

from django.conf import settings
from django.http import QueryDict
from django.http import HttpResponse
from django.utils.encoding import smart_str

from talentmap_api.fsbid.services import common as services
from talentmap_api.fsbid.services import client as client_services
import talentmap_api.fsbid.services.agenda_item_validator as ai_validator
from talentmap_api.common.common_helpers import ensure_date, sort_legs

AGENDA_API_ROOT = settings.AGENDA_API_URL
PANEL_API_ROOT = settings.PANEL_API_URL
CLIENTS_ROOT_V2 = settings.CLIENTS_API_V2_URL
API_ROOT = settings.WS_ROOT_API_URL

logger = logging.getLogger(__name__)


def get_single_agenda_item(jwt_token=None, pk=None):
    '''
    Get single agenda item
    '''

    args = {
        "uri": "",
        "query": {'aiseqnum': pk},
        "query_mapping_function": convert_agenda_item_query,
        "jwt_token": jwt_token,
        "mapping_function": fsbid_single_agenda_item_to_talentmap_single_agenda_item,
        "count_function": None,
        "base_url": "/api/v1/fsbid/agenda/",
        "api_root": AGENDA_API_ROOT,
    }

    agenda_item = services.send_get_request(
        **args
    )

    ai_return = pydash.get(agenda_item, 'results[0]') or None

    if ai_return:
        # Get Vice/Vacancy data
        pos_seq_nums = []
        legs = pydash.get(ai_return, "legs")
        for leg in legs:
            if ('ail_pos_seq_num' in leg) and (leg["ail_pos_seq_num"] is not None):
                pos_seq_nums.append(leg["ail_pos_seq_num"])
        vice_lookup = get_vice_data(pos_seq_nums, jwt_token)

        # Add Vice/Vacancy data to AI for AIM page
        for leg in legs:
            if 'ail_pos_seq_num' in leg:
                if leg["is_separation"]:
                    leg["vice"] = {}
                else:
                    leg["vice"] = vice_lookup.get(leg["ail_pos_seq_num"]) or {}
    return ai_return


def get_agenda_items(jwt_token=None, query={}, host=None):
    '''
    Get agenda items
    '''
    from talentmap_api.fsbid.services.agenda_employees import get_agenda_employees

    args = {
        "uri": "",
        "query": query,
        "query_mapping_function": convert_agenda_item_query,
        "jwt_token": jwt_token,
        "mapping_function": fsbid_single_agenda_item_to_talentmap_single_agenda_item,
        "count_function": None,
        "base_url": "/api/v1/agendas/",
        "host": host,
        "use_post": False,
        "api_root": AGENDA_API_ROOT,
    }

    agenda_items = services.send_get_request(
        **args
    )

    employeeQuery = QueryDict(f"limit=1&page=1&perdet={query.get('perdet', None)}")
    employee = get_agenda_employees(employeeQuery, jwt_token, host)
    return {
        "employee": employee,
        "results": agenda_items,
    }

def create_agenda(query={}, jwt_token=None, host=None):
    '''
    Create agenda
    '''
    hru_id = jwt.decode(jwt_token, verify=False).get('sub')
    query['hru_id'] = hru_id
    logger.info(f"1. query --------------------------------------------------- {query}")
    logger.info('2. validating ai ---------------------------------------------------')
    ai_validation = ai_validator.validate_agenda_item(query)
    logger.info(f"2a. ai valid {ai_validation['allValid']}")
    if not ai_validation['allValid']:
        return ai_validation
    logger.info('3. calling pmi ---------------------------------------------------')
    panel_meeting_item = create_panel_meeting_item(query, jwt_token)
    logger.info(f"3a. pmi return {panel_meeting_item}")
    pmi_seq_num = pydash.get(panel_meeting_item, '[0].pmi_seq_num')

    if pmi_seq_num:
        query['pmiseqnum'] = pmi_seq_num
        logger.info('4. calling ai ---------------------------------------------------')
        agenda_item = create_agenda_item(query, jwt_token)
        logger.info(f"4a. ai return {agenda_item}")
        ai_seq_num = pydash.get(agenda_item, '[0].ai_seq_num')
        if ai_seq_num:
            query['aiseqnum'] = ai_seq_num
            if pydash.get(query, 'agendaLegs'):
                logger.info('5. calling ail ---------------------------------------------------')
                for x in query['agendaLegs']:
                    agenda_item_leg = create_agenda_item_leg(x, query, jwt_token)
                    logger.info(f"5a. ail return {agenda_item_leg}")
        else:
            logger.error("AI create failed")
    else:
        logger.error("PMI create failed")


def create_panel_meeting_item(query, jwt_token):
    '''
    Create PMI
    '''
    args = {
        "uri": "v1/panels/meetingItem",
        "query": query,
        "query_mapping_function": convert_panel_meeting_item_query,
        "jwt_token": jwt_token,
        "mapping_function": "",
    }

    return services.get_results_with_post(
        **args
    )


def create_agenda_item(query, jwt_token):
    '''
    Create AI
    '''
    args = {
        "uri": "v1/agendas",
        "query": query,
        "query_mapping_function": convert_create_agenda_item_query,
        "jwt_token": jwt_token,
        "mapping_function": "",
    }

    return services.get_results_with_post(
        **args
    )


def create_agenda_item_leg(data, query, jwt_token):
    '''
    Create AIL
    '''
    aiseqnum = query["aiseqnum"]
    args = {
        "uri": f"v1/agendas/{aiseqnum}/legs",
        "query": query,
        "query_mapping_function": partial(convert_agenda_item_leg_query, leg=data),
        "jwt_token": jwt_token,
        "mapping_function": ""
    }

    return services.get_results_with_post(
        **args
    )


def get_agenda_item_history_csv(query, jwt_token, host, limit=None):

    args = {
        "uri": "",
        "query": query,
        "query_mapping_function": convert_agenda_item_query,
        "jwt_token": jwt_token,
        "mapping_function": fsbid_single_agenda_item_to_talentmap_single_agenda_item,
        "host": host,
        "use_post": False,
        "base_url": AGENDA_API_ROOT,
    }

    data = services.send_get_csv_request(
        **args
    )

    response = services.get_aih_csv(data, f"agenda_item_history_{query.get('client')}")

    return response


# Placeholder. Isn't used and doesn't work.
def get_agenda_items_count(query, jwt_token, host=None, use_post=False):
    '''
    Gets the total number of agenda items for a filterset
    '''
    args = {
        "uri": "",
        "query": query,
        "query_mapping_function": convert_agenda_item_query,
        "jwt_token": jwt_token,
        "host": host,
        "use_post": False,
        "api_root": AGENDA_API_ROOT,
    }
    return services.send_count_request(**args)


def convert_agenda_item_query(query):
    '''
    Converts TalentMap filters into FSBid filters
    '''
    values = {
        # Pagination
        "rp.pageNum": int(query.get("page", 1)),
        "rp.pageRows": int(query.get("limit", 1000)),
        "rp.columns": None,
        "rp.orderBy": services.sorting_values(query.get("ordering", "agenda_id")),
        "rp.filter": services.convert_to_fsbid_ql([
            {'col': 'aiperdetseqnum', 'val': query.get("perdet", None)},
            {'col': 'aiseqnum', 'val': query.get("aiseqnum", None)}
        ]),
    }

    valuesToReturn = pydash.omit_by(values, lambda o: o is None or o == [])

    return urlencode(valuesToReturn, doseq=True, quote_via=quote)


def fsbid_single_agenda_item_to_talentmap_single_agenda_item(data):
    agendaStatusAbbrev = {
        "Approved": "APR",
        "Deferred - Proposed Position": "XXX",
        "Disapproved": "DIS",
        "Deferred": "DEF",
        "Held": "HLD",
        "Move to ML/ID": "MOV",
        "Not Ready": "NR",
        "Out of Order": "OOO",
        "PIP": "PIP",
        "Ready": "RDY",
        "Withdrawn": "WDR"
    }
    legsToReturn = []
    assignment = fsbid_aia_to_talentmap_aia(
        pydash.get(data, "agendaAssignment[0]", {})
    )
    legs = (list(map(
        fsbid_legs_to_talentmap_legs, pydash.get(data, "agendaLegs", [])
    )))
    sortedLegs = sort_legs(legs)
    legsToReturn.extend([assignment])
    legsToReturn.extend(sortedLegs)
    statusFull = pydash.get(data, "aisdesctext") or None
    updaters = pydash.get(data, "updaters") or None
    reportCategory = {
        "code": pydash.get(data, "Panel[0].pmimiccode") or None,
        "desc_text": pydash.get(data, "Panel[0].micdesctext") or None,
    }
    panelMeetingSeqNum = str(int(pydash.get(data, "Panel[0].pmseqnum"))) if pydash.get(data, "Panel[0].pmseqnum") else ""
    if updaters:
        updaters = fsbid_ai_creators_updaters_to_talentmap_ai_creators_updaters(updaters[0])

    creators = pydash.get(data, "creators") or None
    if creators:
        creators = fsbid_ai_creators_updaters_to_talentmap_ai_creators_updaters(creators[0])
    return {
        "id": pydash.get(data, "aiseqnum") or None,
        "pmi_official_item_num": pydash.get(data, "pmiofficialitemnum") or None,
        "remarks": services.parse_agenda_remarks(pydash.get(data, "remarks") or []),
        "panel_date": ensure_date(pydash.get(data, "Panel[0].pmddttm"), utc_offset=-5),
        "meeting_category": pydash.get(data, "Panel[0].pmimiccode") or None,
        "panel_date_type": pydash.get(data, "Panel[0].pmtcode") or None,
        "panel_meeting_seq_num": panelMeetingSeqNum,
        "status_full": statusFull,
        "status_short": agendaStatusAbbrev.get(statusFull, None),
        "report_category": reportCategory,
        "perdet": str(int(pydash.get(data, "aiperdetseqnum"))) or None,
        "assignment": assignment,
        "legs": legsToReturn,
        "update_date": ensure_date(pydash.get(data, "update_date"), utc_offset=-5),  # TODO - find this date
        "modifier_name": pydash.get(data, "aiupdateid") or None,  # TODO - this is only the id
        "modifier_date": ensure_date(pydash.get(data, "aiupdatedate"), utc_offset=-5) or None,
        "creator_name": pydash.get(data, "aiitemcreatorid") or None,  # TODO - this is only the id
        "creator_date": ensure_date(pydash.get(data, "aicreatedate"), utc_offset=-5) or None,
        "creators": creators,
        "updaters": updaters,
        "user": {},
    }


def fsbid_agenda_items_to_talentmap_agenda_items(data, jwt_token=None):
    ai_id = data.get("aiseqnum", None)

    agenda_item = get_single_agenda_item(jwt_token, ai_id)

    return {
        "id": data.get("aiseqnum", None),
        **agenda_item,
    }


def fsbid_legs_to_talentmap_legs(data):
    # Temporary mapping helper. FSBid will handle this
    tf_mapping = {
        "8150": "Post to Post without Home Leave (Direct Transfer)",
        "8151": "Post to Post with Home Leave",
        "8152": "Post to U.S. with Home Leave",
        "8153": "Post to U.S. without Home Leave (Direct Transfer to U.S.)",
        "8154": "Separation from the Service",
        "8155": "U.S. to Post",
        "8156": "Initial Appointment to Post from U.S.",
        "8157": "Initial Appointment to U.S.",
        "8158": "Initial Appointment from Overseas",
        "8159": "Intra U.S. (Transfer from one U.S. Location to Another U.S. Location)",
        "8160": "Round Trip Home Leave",
        "8161": "Advance Travel of Dependents",
        "8162": "Remains of Deceased Dependents",
        "8169": "SMA Travel",
    }

    def map_tf(tf=None):
        return pydash.get(tf_mapping, tf, None)

    tod_code = pydash.get(data, "ailtodcode")
    tod_short_desc = pydash.get(data, "todshortdesc")
    tod_long_desc = pydash.get(data, "toddesctext")
    # only custom/other TOD will have other_text
    tod_other_text = pydash.get(data, "ailtodothertext")
    tod_months = pydash.get(data, "ailtodmonthsnum")
    is_other_tod = True if (tod_code == 'X') and (tod_other_text) else False
    tod_is_active = pydash.get(data, "todstatuscode") == "A"
    # legacy and custom/other TOD Agenda Item Legs will not render as a dropdown
    tod_is_dropdown = (tod_code != "X") and (tod_is_active is True)
    city = pydash.get(data, 'ailcitytext') or ''
    country_state = pydash.get(data, 'ailcountrystatetext') or ''
    location = f"{city}{', ' if (city and country_state) else ''}{country_state}"
    lat_code = pydash.get(data, 'aillatcode')

    res = {
        "id": pydash.get(data, "ailaiseqnum", None),
        "ail_seq_num": pydash.get(data, "ailseqnum", None),
        "ail_pos_seq_num": pydash.get(data, "ailposseqnum", None),
        "pos_title": pydash.get(data, "agendaLegPosition[0].postitledesc", None),
        "pos_num": pydash.get(data, "agendaLegPosition[0].posnumtext", None),
        "org": pydash.get(data, "agendaLegPosition[0].posorgshortdesc", None),
        "eta": pydash.get(data, "ailetadate", None),
        "ted": pydash.get(data, "ailetdtedsepdate", None),
        "tod": tod_code,
        "tod_is_dropdown": tod_is_dropdown,
        "tod_months": tod_months if is_other_tod else None, # only a custom/other TOD should have months
        "tod_short_desc": tod_other_text if is_other_tod else tod_short_desc,
        "tod_long_desc": tod_other_text if is_other_tod else tod_long_desc,
        "grade": pydash.get(data, "agendaLegPosition[0].posgradecode", None),
        "languages": services.parseLanguagesToArr(pydash.get(data, "agendaLegPosition[0]", None)),
        "action": pydash.get(data, "latabbrdesctext", None),
        "travel": map_tf(pydash.get(data, "ailtfcd", None)),
        "is_separation": False,
        "pay_plan": pydash.get(data, "agendaLegPosition[0].pospayplancode", None),
        "pay_plan_desc": pydash.get(data, "agendaLegPosition[0].pospayplandesc", None),
    }
    
    # Remove fields not applicable for separation leg action types
    separation_types = ['H', 'M', 'N', 'O', 'P']
    if lat_code in separation_types:
        res['is_separation'] = True
        res['pos_title'] = pydash.get(data, 'latdesctext')
        res['pos_num'] = '-'
        res['eta'] = '-'
        res['tod'] = None
        res['tod_short_desc'] = '-' 
        res['tod_months'] = '-' 
        res['tod_long_desc'] = '-' 
        res['grade'] = '-'
        res['languages'] = '-'
        res['org'] = location
        res['separation_location'] = {
                "city": city,
                "country": country_state,
                "code": pydash.get(data, 'aildsccd'),
            }

    return res


def fsbid_ai_creators_updaters_to_talentmap_ai_creators_updaters(data):
    empUser = pydash.get(data, "empUser") or None
    if empUser:
        empUser = (list(map(lambda emp_user: {
            "emp_user_first_name": emp_user["perpiifirstname"],
            "emp_user_last_name": emp_user["perpiilastname"],
            "emp_user_seq_num": emp_user["perpiiseqnum"],
            "emp_user_middle_name": emp_user["perpiimiddlename"],
            "emp_user_suffix_name": emp_user["perpiisuffixname"],
            "perdet_seqnum": emp_user["perdetseqnum"],
            "per_desc": emp_user["persdesc"],
        }, empUser)))[0]

    return {
        "emp_seq_num": pydash.get(data, "hruempseqnbr"),
        "neu_id": pydash.get(data, "neuid"),
        "hru_id": pydash.get(data, "hruid"),
        "last_name": pydash.get(data, "neulastnm"),
        "first_name": pydash.get(data, "neufirstnm"),
        "middle_name": pydash.get(data, "neumiddlenm"),
        "emp_user": empUser
    }

# aia = agenda item assignment
def fsbid_aia_to_talentmap_aia(data):
    tod_code = pydash.get(data, "asgdtodcode")
    tod_months = pydash.get(data, "asgdtodmonthsnum")
    tod_other_text = pydash.get(data, "asgdtodothertext") # only custom/other TOD should have months and other_text
    tod_short_desc = pydash.get(data, "todshortdesc")
    tod_long_desc = pydash.get(data, "toddesctext")
    is_other_tod = True if (tod_code == 'X') and (tod_other_text) else False

    return {
        "id": pydash.get(data, "asgdasgseqnum", None),
        "pos_title": pydash.get(data, "position[0].postitledesc", None),
        "pos_num": pydash.get(data, "position[0].posnumtext", None),
        "org": pydash.get(data, "position[0].posorgshortdesc", None),
        "eta": pydash.get(data, "asgdetadate", None),
        "ted": pydash.get(data, "asgdetdteddate", None),
        "tod": tod_code,
        "tod_months": tod_months if is_other_tod else None, # only custom/other TOD should have months and other_text
        "tod_short_desc": tod_other_text if is_other_tod else tod_short_desc,
        "tod_long_desc": tod_other_text if is_other_tod else tod_long_desc,
        "grade": pydash.get(data, "position[0].posgradecode", None),
        "languages": services.parseLanguagesToArr(pydash.get(data, "position[0]", None)),
        "travel": "-",
        "action": "-",
        "is_separation": False,
        "pay_plan": pydash.get(data, "position[0].pospayplancode", None),
        "pay_plan_desc": pydash.get(data, "position[0].pospayplandesc", None),
    }


def get_agenda_statuses(query, jwt_token):
    '''
    Get agenda statuses
    '''

    args = {
        "uri": "references/statuses",
        "query": query,
        "query_mapping_function": convert_agenda_statuses_query,
        "jwt_token": jwt_token,
        "mapping_function": fsbid_to_talentmap_agenda_statuses,
        "count_function": None,
        "base_url": "/api/v1/agendas/",
        "api_root": AGENDA_API_ROOT,
    }

    agenda_statuses = services.send_get_request(
        **args
    )

    return agenda_statuses


def convert_agenda_statuses_query(query):
    '''
    Converts TalentMap query into FSBid query
    '''

    values = {
        "rp.pageNum": int(query.get("page", 1)),
        "rp.pageRows": int(query.get("limit", 1000)),
    }

    valuesToReturn = pydash.omit_by(values, lambda o: o is None or o == [])

    return urlencode(valuesToReturn, doseq=True, quote_via=quote)


def convert_panel_meeting_item_query(query):
    '''
    Converts TalentMap query into FSBid query
    '''
    creator_id = pydash.get(query, "hru_id")
    return {
        "pmimiccode": pydash.get(query, "panelMeetingCategory") or "D",
        "pmipmseqnum": int(pydash.get(query, "panelMeetingId")),
        "pmicreateid": creator_id,
        "pmiupdateid": creator_id,
    }


def convert_create_agenda_item_query(query):
    '''
    Converts TalentMap query into FSBid query
    '''
    user_id = pydash.get(query, "hru_id")
    return {
        "aipmiseqnum": pydash.get(query, "pmiseqnum", ""),
        "aiempseqnbr": pydash.get(query, "personId", ""),
        "aiperdetseqnum": pydash.get(query, "personDetailId", ""),
        "aiaiscode": pydash.get(query, "agendaStatusCode", ""),
        "aitoddesctext": None,
        "aitodcode": None,
        "aiasgseqnum": pydash.get(query, "assignmentId", ""),
        "aiasgdrevisionnum": pydash.get(query, "assignmentVersion", ""),
        "aicombinedtodmonthsnum": None,
        "aicombinedtodothertext": None,
        "aicombinedremarktext": None,
        "aicorrectiontext": None,
        "ailabeltext": None,
        "aisorttext": None,
        "aicreateid": user_id,
        "aicreatedate": None,
        "aiupdateid": user_id,
        "aiseqnumref": None,
        "aiitemcreatorid": user_id,
    }

def convert_agenda_item_leg_query(query, leg={}):
    '''
    Converts TalentMap query into FSBid query
    '''

    user_id = pydash.get(query, "hru_id")

    tod_code = pydash.get(leg, "tod", ""),
    tod_long_desc = pydash.get(leg, "tod_long_desc")
    is_other_tod = True if (tod_code == 'X') and (tod_long_desc) else False
    tod_months = pydash.get(leg, "tod_months")
    return {
        "ailaiseqnum": pydash.get(query, "aiseqnum"),
        "aillatcode": pydash.get(leg, "legActionType", ""),
        "ailtfcd": pydash.get(leg, "travelFunctionCode", ""),
        "ailcpid": int(pydash.get(leg, "cpId") or 0) or None,
        "ailempseqnbr": int(pydash.get(query, "personId") or 0) or None,
        "ailperdetseqnum": int(pydash.get(query, "personDetailId") or 0) or None,
        "ailposseqnum": int(pydash.get(leg, "posSeqNum") or 0) or None,
        "ailtodcode": pydash.get(leg, "tod", ""),
        "ailtodmonthsnum": tod_months if is_other_tod else None, # only custom/other TOD should pass back months and other_text
        "ailtodothertext": tod_long_desc if is_other_tod else None, # only custom/other TOD should pass back months and other_text
        "ailetadate": None,
        "ailetdtedsepdate": pydash.get(leg, "legEndDate", None),
        "aildsccd": pydash.get(leg, "separation_location.code") or None,
        "ailcitytext": pydash.get(leg, "separation_location.city") or None,
        "ailcountrystatetext": pydash.get(leg, "separation_location.description") or None,
        "ailusind": None,
        "ailemprequestedsepind": None,
        "ailcreateid": user_id,
        "ailupdateid": user_id,
        "ailasgseqnum": int(pydash.get(leg, "legAssignmentId") or 0) or None,
        "ailasgdrevisionnum": int(pydash.get(leg, "legAssignmentVersion") or 0) or None,
        "ailsepseqnum": None,
        "ailsepdrevisionnum": None,
    }


def fsbid_to_talentmap_agenda_statuses(data):
    # hard_coded are the default data points (opinionated EP)
    # add_these are the additional data points we want returned

    hard_coded = ['code', 'abbr_desc_text', 'desc_text']

    add_these = []

    cols_mapping = {
        'code': 'aiscode',
        'abbr_desc_text': 'aisabbrdesctext',
        'desc_text': 'aisdesctext',
    }

    add_these.extend(hard_coded)

    return services.map_return_template_cols(add_these, cols_mapping, data)


def get_agenda_ref_remarks(query, jwt_token):
    '''
    Get agenda reference remarks
    '''
    args = {
        "uri": "references/remarks",
        "query": query,
        "query_mapping_function": None,
        "jwt_token": jwt_token,
        "mapping_function": fsbid_to_talentmap_agenda_remarks_ref,
        "count_function": None,
        "base_url": "/api/v1/agendas/",
        "api_root": AGENDA_API_ROOT,
    }

    agenda_remarks = services.send_get_request(
        **args
    )

    return agenda_remarks


def fsbid_to_talentmap_agenda_remarks(data):
    # hard_coded are the default data points (opinionated EP)
    # add_these are the additional data points we want returned

    hard_coded = ['seq_num', 'rc_code', 'order_num', 'short_desc_text', 'mutually_exclusive_ind', 'text', 'active_ind', 'remark_inserts', 'ref_text', 'user_remark_inserts']

    add_these = []

    cols_mapping = {
        'seq_num': 'rmrkseqnum',
        'rc_code': 'rmrkrccode',
        'order_num': 'rmrkordernum',
        'short_desc_text': 'rmrkshortdesctext',
        'mutually_exclusive_ind': 'rmrkmutuallyexclusiveind',
        'text': 'rmrktext',
        'ref_text': 'refrmrktext',
        'active_ind': 'rmrkactiveind',
        'remark_inserts': 'RemarkInserts',
        'user_remark_inserts': 'refrmrkinsertions'
    }

    add_these.extend(hard_coded)

    return services.map_return_template_cols(add_these, cols_mapping, data)

def fsbid_to_talentmap_agenda_remarks_ref(data):
    # hard_coded are the default data points (opinionated EP)
    # add_these are the additional data points we want returned

    hard_coded = [
        'seq_num', 
        'rc_code', 
        'order_num', 
        'short_desc_text', 
        'mutually_exclusive_ind', 
        'text', 
        'active_ind', 
        'remark_inserts', 
        'ref_text', 
        'update_date',
        'update_id',
        'create_date',
        'create_id',
    ]

    add_these = []

    cols_mapping = {
        'seq_num': 'rmrkseqnum',
        'rc_code': 'rmrkrccode',
        'order_num': 'rmrkordernum',
        'short_desc_text': 'rmrkshortdesctext',
        'mutually_exclusive_ind': 'rmrkmutuallyexclusiveind',
        'text': 'rmrktext',
        'ref_text': 'rmrktext',
        'active_ind': 'rmrkactiveind',
        'update_date': 'rmrkupdatedate',
        'update_id': 'rmrkupdateid',
        'create_date': 'rmrkcreatedate',
        'create_id': 'rmrkcreateid',
        'remark_inserts': 'RemarkInserts'
    }

    add_these.extend(hard_coded)

    return services.map_return_template_cols(add_these, cols_mapping, data)


def get_agenda_remark_categories(query, jwt_token):
    '''
    Get agenda remark categories
    '''
    args = {
        "uri": "references/remark-categories",
        "query": query,
        "query_mapping_function": None,
        "jwt_token": jwt_token,
        "mapping_function": fsbid_to_talentmap_agenda_remark_categories,
        "count_function": None,
        "base_url": "/api/v1/agendas/",
        "api_root": AGENDA_API_ROOT,
    }

    agenda_remark_categories = services.send_get_request(
        **args
    )

    return agenda_remark_categories


def fsbid_to_talentmap_agenda_remark_categories(data):
    # hard_coded are the default data points (opinionated EP)
    # add_these are the additional data points we want returned

    hard_coded = ['code', 'desc_text']

    add_these = []

    cols_mapping = {
        'code': 'rccode',
        'desc_text': 'rcdesctext'
    }

    add_these.extend(hard_coded)

    return services.map_return_template_cols(add_these, cols_mapping, data)


def get_agenda_leg_action_types(query, jwt_token):
    '''
    Get agenda leg-action-types
    '''
    args = {
        "uri": "references/leg-action-types",
        "query": query,
        "query_mapping_function": None,
        "jwt_token": jwt_token,
        "mapping_function": fsbid_to_tmap_agenda_leg_action_types,
        "count_function": None,
        "base_url": "/api/v1/agendas/",
        "api_root": AGENDA_API_ROOT,
    }

    agenda_leg_action_types = services.send_get_request(
        **args
    )

    return agenda_leg_action_types

def fsbid_to_tmap_agenda_leg_action_types(data):
    separation_types = ['H', 'M', 'N', 'O', 'P']
    code = data.get('latcode')

    return {
        'code': code,
        'abbr_desc_text': data.get('latabbrdesctext'),
        'desc_text': data.get('latdesctext'),
        'is_separation': True if code in separation_types else False,
    }


def convert_agendas_by_panel_query(query):
    '''
    Converts TalentMap query into FSBid query
    '''
    values = {
        "rp.pageNum": int(0),
        "rp.pageRows": int(0),
        "rp.orderBy": 'pmiofficialitemnum',
    }

    valuesToReturn = pydash.omit_by(values, lambda o: o is None or o == [])

    return urlencode(valuesToReturn, doseq=True, quote_via=quote)


def get_agendas_by_panel(pk, jwt_token):
    '''
    Get agendas for panel meeting
    '''
    args = {
        "uri": f"{pk}/agendas",
        "query": {},
        "query_mapping_function": convert_agendas_by_panel_query,
        "jwt_token": jwt_token,
        "mapping_function": fsbid_single_agenda_item_to_talentmap_single_agenda_item,
        "count_function": None,
        "base_url": "/api/v1/panels/",
        "api_root": PANEL_API_ROOT,
    }
    agendas_by_panel = services.send_get_request(
        **args
    )
    perdets = list(map(lambda x: x["perdet"], agendas_by_panel["results"]))
    ad_id = jwt.decode(jwt_token, verify=False).get('unique_name')
    query = {
        "ad_id": ad_id,
        "perdet_seq_num": perdets,
        "currentAssignmentOnly": "true",
        "page": 1,
        "limit": 1000,
    }
    clients = services.send_get_request(
        "",
        query,
        client_services.convert_client_query,
        jwt_token,
        client_services.fsbid_clients_to_talentmap_clients,
        client_services.get_clients_count,
        "/api/v2/clients/",
        None,
        CLIENTS_ROOT_V2,
    )
    clients_lookup = {}
    for client in clients.get("results") or []:
        perdet = client["perdet_seq_number"]
        clients_lookup[perdet] = client

    # get vice data to add to agendas_by_panel
    pos_seq_nums = []
    for agenda in agendas_by_panel["results"]:
        legs = pydash.get(agenda, "legs")
        for leg in legs:
            if ('ail_pos_seq_num' in leg) and (leg["ail_pos_seq_num"] is not None):
                pos_seq_nums.append(leg["ail_pos_seq_num"])
    vice_lookup = get_vice_data(pos_seq_nums, jwt_token)

    for agenda in agendas_by_panel["results"]:
        client = clients_lookup.get(agenda["perdet"]) or {}
        agenda["user"] = client
        legs = pydash.get(agenda, "legs")
        # append vice data to add to agendas_by_panel
        for leg in legs:
            if 'ail_pos_seq_num' in leg:
                if leg["is_separation"]:
                    leg["vice"] = {} 
                else:
                    leg["vice"] = vice_lookup.get(leg["ail_pos_seq_num"]) or {}
    return agendas_by_panel

def get_agendas_by_panel_export(pk, jwt_token, host=None):
    '''
    Get agendas for panel meeting export
    '''
    mapping_subset = {
        'default': 'None Listed',
        'wskeys': {
            'agendaAssignment[0].position[0].postitledesc': {},
            'agendaAssignment[0].position[0].posnumtext': {
                'transformFn': lambda x: smart_str("=\"%s\"" % x),
            },
            'agendaAssignment[0].position[0].posorgshortdesc': {},
            'agendaAssignment[0].asgdetadate': {
                'transformFn': services.process_dates_csv,
            },
            'agendaAssignment[0].asgdetdteddate': {
                'transformFn': services.process_dates_csv,
            },
            'agendaAssignment[0].asgdtoddesctext': {},
            'agendaAssignment[0].position[0].posgradecode': {
                'transformFn': lambda x: smart_str("=\"%s\"" % x),
            },
            'Panel[0].pmddttm': {
                'transformFn': services.process_dates_csv,
            },
            'aisdesctext': {},
            'remarks': {
                'transformFn': services.process_remarks_csv,
            },
        }
    }
    args = {
        "uri": f"{pk}/agendas",
        "query": {},
        "query_mapping_function": convert_agendas_by_panel_query,
        "jwt_token": jwt_token,
        "mapping_function": partial(services.csv_fsbid_template_to_tm, mapping=mapping_subset),
        "count_function": None,
        "base_url": "/api/v1/panels/",
        "api_root": PANEL_API_ROOT,
        "host": host,
        "use_post": False,
    }

    data = services.send_get_request(**args)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f"attachment; filename=panel_meeting_agendas_{datetime.now().strftime('%Y_%m_%d_%H%M%S')}.csv"

    writer = csv.writer(response, csv.excel)
    response.write(u'\ufeff'.encode('utf8'))

    writer.writerow([
        smart_str(u"Position Title"),
        smart_str(u"Position Number"),
        smart_str(u"Org"),
        smart_str(u"ETA"),
        smart_str(u"TED"),
        smart_str(u"TOD"),
        smart_str(u"Grade"),
        smart_str(u"Panel Date"),
        smart_str(u"Status"),
        smart_str(u"Remarks"),
    ])

    writer.writerows(data['results'])

    return response

def get_vice_data(pos_seq_nums, jwt_token):
    args = {
        "uri": "v1/vice-positions/",
        "jwt_token": jwt_token,
        "query": pos_seq_nums,
        "query_mapping_function": vice_query_mapping,
        "mapping_function": None,
        "count_function": None,
        "base_url": "",
        "host": None,
        "api_root": API_ROOT
    }
    vice_req = services.send_get_request(
        **args
    )
    vice_data = pydash.get(vice_req, 'results')

    vice_lookup = {}
    for vice in vice_data or []:
        if "pos_seq_num" in vice:
            pos_seq = vice["pos_seq_num"]
            # check for multiple incumbents in same postion
            if pos_seq in vice_lookup:
                vice_lookup[pos_seq] = {
                    "pos_seq_num": pos_seq,
                    "emp_first_name": "Multiple",
                    "emp_last_name": "Incumbents"
                }
            else:
                vice_lookup[pos_seq] = vice

    return vice_lookup

def vice_query_mapping(pos_seq_nums):
    pos_seq_nums_string = ','.join(map(lambda x: str(x), list(set(pos_seq_nums))))
    filters = services.convert_to_fsbid_ql([
        {'col': 'pos_seq_num', 'com': 'IN', 'val': pos_seq_nums_string},
    ])
    values = {
        "rp.filter": filters,
        "rp.pageNum": int(0),
        "rp.pageRows": int(0),
    }
    valuesToReturn = pydash.omit_by(values, lambda o: o is None or o == [])
    return urlencode(valuesToReturn, doseq=True, quote_via=quote)
