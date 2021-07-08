import logging
import pydash
import maya
from urllib.parse import urlencode, quote
from functools import partial
from copy import deepcopy

import requests  # pylint: disable=unused-import

from django.conf import settings
from django.core.exceptions import PermissionDenied

from talentmap_api.bidding.models import BidHandshakeCycle

from talentmap_api.common.common_helpers import ensure_date, validate_values

import talentmap_api.fsbid.services.bid as bid_services
import talentmap_api.fsbid.services.cdo as cdoservices
import talentmap_api.bidding.services.bidhandshake as bh_services
import talentmap_api.fsbid.services.common as services
import talentmap_api.fsbid.services.classifications as classifications_services
import talentmap_api.fsbid.services.employee as empservices

from talentmap_api.available_positions.models import AvailablePositionRanking

logger = logging.getLogger(__name__)

API_ROOT = settings.FSBID_API_URL
CP_API_ROOT = settings.CP_API_URL


def get_bureau_position(id, jwt_token):
    '''
    Gets an indivdual bureau position by id
    '''
    return services.get_individual(
        "availablePositions",
        id,
        convert_bp_query,
        jwt_token,
        fsbid_bureau_positions_to_talentmap,
    )


def get_bureau_positions(query, jwt_token, host=None):
    '''
    Gets all bureau positions
    '''
    return services.send_get_request(
        "availablePositions",
        query,
        convert_bp_query,
        jwt_token,
        fsbid_bureau_positions_to_talentmap,
        get_bureau_positions_count,
        "/api/v1/fsbid/bureau/positions/",
        host,
    )


def get_bureau_positions_count(query, jwt_token, host=None):
    '''
    Gets the total number of bureau positions for a filterset
    '''
    return services.send_count_request("availablePositionsCount", query, convert_bp_query, jwt_token, host)


def get_bureau_positions_csv(query, jwt_token, host=None, limit=None, includeLimit=False):
    data = services.send_get_csv_request(
        "availablePositions",
        query,
        convert_bp_query,
        jwt_token,
        fsbid_bureau_positions_to_talentmap,
        API_ROOT,
    )

    count = get_bureau_positions_count(query, jwt_token)
    response = services.get_ap_and_pv_csv(data, "cycle_positions", True)
    return response


def get_bureau_position_bids(id, query, jwt_token, host):
    '''
    Gets all bids on an indivdual bureau position by id
    '''

    hasBureauPermissions = empservices.has_bureau_permissions(id, jwt_token)
    hasOrgPermissions = empservices.has_org_permissions(id, jwt_token)
    if not (hasBureauPermissions or hasOrgPermissions):
        raise PermissionDenied()

    new_query = deepcopy(query)
    new_query["id"] = id
    active_perdet = bh_services.get_position_handshake_data(id)['active_handshake_perdet']
    return services.get_results(
        "bidders",
        new_query,
        convert_bp_bids_query,
        jwt_token,
        partial(fsbid_bureau_position_bids_to_talentmap, jwt=jwt_token, cp_id=id, active_perdet=active_perdet),
        CP_API_ROOT,
    )

def get_bureau_position_bids_csv(self, id, query, jwt_token, host):
    '''
    Gets all bids on an indivdual bureau position by id for export
    '''

    hasBureauPermissions = empservices.has_bureau_permissions(id, jwt_token)
    hasOrgPermissions = empservices.has_org_permissions(id, jwt_token)
    if not (hasBureauPermissions or hasOrgPermissions):
        raise PermissionDenied()

    new_query = deepcopy(query)
    new_query["id"] = id
    active_perdet = bh_services.get_position_handshake_data(id)['active_handshake_perdet']
    data = services.send_get_csv_request(
        "bidders",
        new_query,
        convert_bp_bids_query,
        jwt_token,
        partial(fsbid_bureau_position_bids_to_talentmap, jwt=jwt_token, cp_id=id, active_perdet=active_perdet),
        CP_API_ROOT,
    )

    pos_num = get_bureau_position(id, jwt_token)["position"]["position_number"]
    filename = f"position_{pos_num}_bidders"
    response = services.get_bidders_csv(self, id, data, filename, True)
    return response

def fsbid_bureau_position_bids_to_talentmap(bid, jwt, cp_id, active_perdet):
    '''
    Formats the response bureau position bids from FSBid
    '''
    cdo = None
    classifications = None
    has_competing_rank = None
    emp_id = bid.get("perdet_seq_num", None)
    if emp_id is not None:
        cdo = cdoservices.single_cdo(jwt, emp_id)
        classifications = classifications_services.get_client_classification(jwt, emp_id)
        has_competing_rank = services.has_competing_rank(jwt, emp_id, cp_id)

    hasHandShakeOffered = False
    if bid.get("handshake_code", None) == "HS":
        hasHandShakeOffered = True
    ted = ensure_date(bid.get("TED", None), utc_offset=-5)

    handshake = bh_services.get_bidder_handshake_data(cp_id, emp_id)

    active_handshake_perdet = None
    if active_perdet:
        if int(active_perdet) == int(emp_id):
            active_handshake_perdet = True
        else:
            active_handshake_perdet = False
    
    fullname = bid.get("full_name", None)
    if fullname:
        fullname = fullname.rstrip(' Nmn')

    return {
        "emp_id": emp_id,
        "name": fullname,
        "email": pydash.get(bid, "userDetails.gal_smtp_email_address_text"),
        "grade": bid.get("grade_code"),
        "skill": f"{bid.get('skill_desc', None)} ({bid.get('skill_code')})",
        "skill_code": bid.get("skill_code", None),
        "language": bid.get("language_txt", None),
        "ted": ted,
        "has_handshake_offered": hasHandShakeOffered,
        "submitted_date": ensure_date(bid.get('ubw_submit_dt'), utc_offset=-5),
        "cdo": cdo,
        "classifications": classifications,
        "has_competing_rank": has_competing_rank,
        "handshake": {
            **handshake,
        },
        "active_handshake_perdet": active_handshake_perdet,
    }


def fsbid_bureau_positions_to_talentmap(bp):
    '''
    Converts the response bureau position from FSBid to a format more in line with the Talentmap position
    '''

    bh_props = bh_services.get_position_handshake_data(bp.get("cp_id", None))

    hasHandShakeOffered = False
    if bp.get("cp_status", None) == "HS":
        hasHandShakeOffered = True
    ted = ensure_date(bp.get("cp_ted_ovrrd_dt", None), utc_offset=-5)
    if ted is None:
        ted = ensure_date(bp.get("ted", None), utc_offset=-5)

    skillSecondary = f"{bp.get('pos_staff_ptrn_skill_desc', None)} ({bp.get('pos_staff_ptrn_skill_code')})"
    skillSecondaryCode = bp.get("pos_staff_ptrn_skill_code", None)
    # If the primary and secondary skills are the same, we interpret this as there being no secondary skill
    if bp.get("pos_skill_code", None) == bp.get("pos_staff_ptrn_skill_code", None):
        skillSecondary = None
        skillSecondaryCode = None
    
    handshake_allowed_date = None
    handshakeCycle = BidHandshakeCycle.objects.filter(cycle_id=bp.get("cycle_id", None))
    if handshakeCycle:
        handshakeCycle = handshakeCycle.first()
        handshake_allowed_date = handshakeCycle.handshake_allowed_date

    return {
        "id": bp.get("cp_id", None),
        "status": None,
        "status_code": bp.get("cp_status", None),
        "ted": ted,
        "posted_date": ensure_date(bp.get("cp_post_dt", None), utc_offset=-5),
        "availability": {
            "availability": None,
            "reason": None
        },
        "position": {
            "id": None,
            "grade": bp.get("pos_grade_code", None),
            "skill": f"{bp.get('pos_skill_desc', None)} ({bp.get('pos_skill_code')})",
            "skill_code": bp.get("pos_skill_code", None),
            "skill_secondary": skillSecondary,
            "skill_secondary_code": skillSecondaryCode,
            "bureau": f"({bp.get('pos_bureau_short_desc', None)}) {bp.get('pos_bureau_long_desc', None)}",
            "bureau_short_desc": f"{bp.get('pos_bureau_short_desc', None)}",
            "organization": f"({bp.get('org_short_desc', None)}) {bp.get('org_long_desc', None)}",
            "tour_of_duty": bp.get("tod", None),
            "classifications": None,
            "representation": None,
            "availability": {
                "availability": None,
                "reason": None
            },
            "position_number": bp.get("position", None),
            "title": bp.get("pos_title_desc", None),
            "is_overseas": None,
            "create_date": None,
            "update_date": ensure_date(bp.get("last_updated_date", None), utc_offset=-5),
            "update_user": bp.get("last_updated_user", None),
            "effective_date": None,
            "posted_date": ensure_date(bp.get("cp_post_dt", None), utc_offset=-5),
            "description": {
                "id": None,
                "last_editing_user": None,
                "is_editable_by_user": None,
                "date_created": None,
                "date_updated": ensure_date(bp.get("ppos_capsule_modify_dt", None), utc_offset=5),
                "content": bp.get("ppos_capsule_descr_txt", None),
                "point_of_contact": None,
                "website": None
            },
            "current_assignment": {
                "user": bp.get("incumbent", None),
                "user_perdet_seq_num": bp.get("incumbent_perdet_seq_num", None),
                "tour_of_duty": bp.get("tod", None),
                "status": None,
                "start_date": None,
                "estimated_end_date": ensure_date(bp.get("ted", None), utc_offset=-5)
            },
            "commuterPost": {
                "description": bp.get("cpn_desc", None),
                "frequency": bp.get("cpn_freq_desc", None),
            },
            "post": {
                "id": None,
                "code": bp.get("pos_location_code", None),
                "tour_of_duty": bp.get("tod", None),
                "post_overview_url": services.get_post_overview_url(bp.get("pos_location_code", None)),
                "post_bidding_considerations_url": services.get_post_bidding_considerations_url(bp.get("pos_location_code", None)),
                "cost_of_living_adjustment": None,
                "differential_rate": bp.get("bt_differential_rate_num", None),
                "danger_pay": bp.get("bt_danger_pay_num", None),
                "rest_relaxation_point": None,
                "has_consumable_allowance": None,
                "has_service_needs_differential": None,
                "obc_id": services.get_obc_id(bp.get("pos_location_code", None)),
                "location": {
                    "country": bp.get("location_country", None),
                    "code": bp.get("pos_location_code", None),
                    "city": bp.get("location_city", None),
                    "state": bp.get("location_state", None),
                },
            },
            "latest_bidcycle": {
                "id": bp.get("cycle_id", None),
                "name": bp.get("cycle_nm_txt", None),
                "cycle_start_date": None,
                "cycle_deadline_date": None,
                "cycle_end_date": None,
                "active": None
            },
            "languages": list(filter(None, [
                services.parseLanguage(bp.get("lang1", None)),
                services.parseLanguage(bp.get("lang2", None)),
            ])),
        },
        "bidcycle": {
            "id": bp.get("cycle_id", None),
            "name": bp.get("cycle_nm_txt", None),
            "cycle_start_date": None,
            "cycle_deadline_date": None,
            "cycle_end_date": None,
            "active": None,
            "handshake_allowed_date": handshake_allowed_date,
        },
        "bid_statistics": [{
            "id": None,
            "total_bids": bp.get("cp_ttl_bidder_qty", None),
            "in_grade": bp.get("cp_at_grd_qty", None),
            "at_skill": bp.get("cp_in_cone_qty", None),
            "in_grade_at_skill": bp.get("cp_at_grd_in_cone_qty", None),
            "has_handshake_offered": hasHandShakeOffered,
            "has_handshake_accepted": None
        }],
        "bid_handshake": bh_props,
        "unaccompaniedStatus": bp.get("us_desc_text", None),
        "isConsumable": bp.get("bt_consumable_allowance_flg", None) == "Y",
        "isServiceNeedDifferential": bp.get("bt_service_needs_diff_flg", None) == "Y",
        "isDifficultToStaff": bp.get("bt_most_difficult_to_staff_flg", None) == "Y",
        "isEFMInside": bp.get("bt_inside_efm_employment_flg", None) == "Y",
        "isEFMOutside": bp.get("bt_outside_efm_employment_flg", None) == "Y",
    }


def convert_bp_query(query, allowed_status_codes=["FP", "OP", "HS"]):
    '''
    Converts TalentMap filters into FSBid filters
    '''
    values = {
        # Pagination
        "request_params.order_by": services.sorting_values(query.get("ordering", None)),
        "request_params.page_index": int(query.get("page", 1)),
        "request_params.page_size": query.get("limit", 25),

        "request_params.cps_codes": services.convert_multi_value(
            validate_values(query.get("cps_codes", "HS,OP,FP"), allowed_status_codes)),
        "request_params.cp_ids": services.convert_multi_value(query.get("id", None)),
        "request_params.assign_cycles": services.convert_multi_value(query.get("is_available_in_bidcycle")),
        "request_params.overseas_ind": services.overseas_values(query),
        "request_params.languages": services.convert_multi_value(query.get("language_codes")),
        "request_params.bureaus": services.convert_multi_value(query.get("position__bureau__code__in")),
        "request_params.grades": services.convert_multi_value(query.get("position__grade__code__in")),
        "request_params.location_codes": services.post_values(query),
        "request_params.danger_pays": services.convert_multi_value(query.get("position__post__danger_pay__in")),
        "request_params.differential_pays": services.convert_multi_value(query.get("position__post__differential_rate__in")),
        "request_params.pos_numbers": services.convert_multi_value(query.get("position__position_number__in", None)),
        "request_params.post_ind": services.convert_multi_value(query.get("position__post_indicator__in")),
        "request_params.tod_codes": services.convert_multi_value(query.get("position__post__tour_of_duty__code__in")),
        "request_params.skills": services.convert_multi_value(query.get("position__skill__code__in")),
        "request_params.us_codes": services.convert_multi_value(query.get("position__us_codes__in")),
        "request_params.cpn_codes": services.convert_multi_value(query.get("position__cpn_codes__in")),
        "request_params.freeText": query.get("q", None),
        "request_params.totalResults": query.get("getCount", 'false'),
    }

    return urlencode({i: j for i, j in values.items() if j is not None}, doseq=True, quote_via=quote)


def convert_bp_bids_query(query):
    '''
    Converts TalentMap filters into FSBid filters
    '''
    values = {
        "request_params.cp_id": query.get("id", None),
        "request_params.order_by": services.sorting_values(query.get("ordering", None)),
        "request_params.handshake_code": query.get("handshake_code", None),
        "request_params.page_size": 500,
        "request_params.page_index": 1,
    }

    return urlencode({i: j for i, j in values.items() if j is not None}, doseq=True, quote_via=quote)

def get_bureau_shortlist_indicator(data):
    '''
    Adds a shortlist indicator field to position results
    '''
    for position in data["results"]:
        position["has_short_list"] = AvailablePositionRanking.objects.filter(cp_id=str(int(position["id"]))).exists()
    return data
