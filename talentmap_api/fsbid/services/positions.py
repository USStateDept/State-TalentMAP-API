import logging
from urllib.parse import urlencode, quote

import pydash
from django.conf import settings

from talentmap_api.fsbid.services import common as services

POSITIONS_V2_ROOT = settings.POSITIONS_API_V2_URL
POSITIONS_ROOT = settings.POSITIONS_API_URL

logger = logging.getLogger(__name__)


def get_position(id, jwt_token):
    '''
    Gets an individual unavailable position by id
    '''
    position = services.send_get_request(
        "Positions",
        {"id": id},
        convert_pos_query,
        jwt_token,
        fsbid_pos_to_talentmap_pos,
        None,
        "/api/v1/fsbid/positions/",
    )

    return pydash.get(position, 'results[0]') or None

def get_positions(query, jwt_token):
    '''
    Gets generic positions
    '''
    positions = services.send_get_request(
        "",
        query,
        convert_position_query,
        jwt_token,
        fsbid_to_talentmap_pos,
        None,
        "/api/v2/positions/",
        None,
        POSITIONS_V2_ROOT,
    )

    return pydash.get(positions, 'results[0]') or None

def fsbid_pos_to_talentmap_pos(pos):
    '''
    Converts the response generic position from FSBid to a format more in line with the Talentmap position
    '''
    empty_score = '--'
    r1 = pos.get("pos_read_proficiency_1_code", None) or empty_score
    s1 = pos.get("pos_speak_proficiency_1_code", None) or empty_score
    l1 = pos.get("pos_language_1_desc", None)
    rep1 = f"{l1} {r1}/{s1}"
    r2 = pos.get("pos_read_proficiency_2_code", None) or empty_score
    s2 = pos.get("pos_speak_proficiency_2_code", None) or empty_score
    l2 = pos.get("pos_language_2_desc", None)
    rep2 = f"{l2} {r2}/{s2}"

    return {
        "id": pos.get("pos_seq_num", None),
        "status": None,
        "status_code": None,
        "ted": None,
        "posted_date": None,
        "availability": {
            "availability": None,
            "reason": None
        },
        "tandem_nbr": None,  # Only appears in tandem searches
        "position": {
            "id": pos.get("pos_seq_num", None),
            "grade": pos.get("pos_grade_code", None),
            "skill": f"{pos.get('pos_skill_desc', '')} {pos.get('pos_skill_code')}",
            "skill_code": pos.get("pos_skill_code", None),
            "skill_secondary": None,
            "skill_secondary_code": None,
            "bureau": f"({pos.get('pos_bureau_short_desc', None)}) {pos.get('pos_bureau_long_desc', None)}",
            "bureau_code": pos.get('pos_bureau_code', None),
            "organization": f"({pos.get('pos_org_short_desc', None)}) {pos.get('pos_org_long_desc', None)}",
            "organization_code": pos.get('pos_org_code', None),
            "tour_of_duty": None,
            "classifications": None,
            "representation": None,
            "availability": {
                "availability": None,
                "reason": None
            },
            "position_number": pos.get("pos_num_text", None),
            "title": pos.get("pos_title_desc", None),
            "is_overseas": None,
            "is_highlighted": None,
            "create_date": pos.get("pos_create_date", None),
            "update_date": pos.get("pos_update_date", None),
            "effective_date": pos.get("pos_effective_date", None),
            "posted_date": None,
            "description": {
                "id": None,
                "last_editing_user": None,
                "is_editable_by_user": None,
                "date_created": None,
                "date_updated": None,
                "content": None,
                "point_of_contact": None,
                "website": None
            },
            "current_assignment": {
                "user": None,
                "tour_of_duty": None,
                "status": None,
                "start_date": None,
                "estimated_end_date": None,
            },
            "commuterPost": {
                "description": None,
                "frequency": None,
            },
            "post": {
                "id": None,
                "code": pos.get("pos_location_code", None),
                "tour_of_duty": None,
                "post_overview_url": None,
                "post_bidding_considerations_url": None,
                "cost_of_living_adjustment": None,
                "differential_rate": pos.get("bt_differential_rate_num", 0),
                "danger_pay": pos.get("bt_danger_pay_num", 0),
                "rest_relaxation_point": None,
                "has_consumable_allowance": None,
                "has_service_needs_differential": None,
                "obc_id": services.get_obc_id(pos.get("pos_location_code", None)),
                "location": {
                    "country": pos.get("location_country", None),
                    "code": pos.get("pos_location_code", None),
                    "city": pos.get("location_city", None),
                    "state": pos.get("location_state", None),
                },
            },
            "latest_bidcycle": {
                "id": None,
                "name": None,
                "cycle_start_date": None,
                "cycle_deadline_date": None,
                "cycle_end_date": None,
                "active": None,
            },
            "languages": [
                {
                    "language": l1,
                    "reading_proficiency": r1,
                    "spoken_proficiency": s1,
                    # Fix this
                    "representation": rep1,
                },
                {
                    "language": l2,
                    "reading_proficiency": r2,
                    "spoken_proficiency": s2,
                    # Fix this
                    "representation": rep2,
                },
            ],
        },
        "bidcycle": {
            "id": None,
            "name": None,
            "cycle_start_date": None,
            "cycle_deadline_date": None,
            "cycle_end_date": None,
            "active": None,
        },
        "bid_statistics": [{
            "id": None,
            "total_bids": None,
            "in_grade": None,
            "at_skill": None,
            "in_grade_at_skill": None,
            "has_handshake_offered": None,
            "has_handshake_accepted": None
        }],
        "unaccompaniedStatus": None,
        "isConsumable": None,
        "isServiceNeedDifferential": None,
        "isDifficultToStaff": None,
        "isEFMInside": None,
        "isEFMOutside": None,
    }


def convert_pos_query(query):
    '''
    Converts TalentMap filters into FSBid filters
    '''

    values = {
        f"request_params.pos_seq_num": query.get("id", None),
        f"request_params.ad_id": query.get("ad_id", None),
        f"request_params.page_index": query.get("page", 1),
        f"request_params.page_size": query.get("limit", None),
        f"request_params.order_by": services.sorting_values(query.get("ordering", None)),
        f"request_params.pos_num_text": query.get("position_num", None),
    }

    return urlencode({i: j for i, j in values.items() if j is not None}, doseq=True, quote_via=quote)

def convert_position_query(query):
    '''
    Converts TalentMap query into FSBid query
    '''

    values = {
        "rp.pageNum": int(query.get("page", 1)),
        "rp.pageRows": int(query.get("limit", 15)),
        "rp.filter": services.convert_to_fsbid_ql([
            {'col': 'posnumtext', 'val': query.get("position_num", None)}
        ]),
    }

    valuesToReturn = pydash.omit_by(values, lambda o: o is None or o == [])

    return urlencode(valuesToReturn, doseq=True, quote_via=quote)

def fsbid_to_talentmap_pos(data):
    # hard_coded are the default data points (opinionated EP)
    # add_these are the additional data points we want returned

    data['languages'] = services.parseLanguagesToArr(data)

    hard_coded = ['pos_seq_num', 'organization', 'position_number', 'grade', 'title', 'languages']

    add_these = []

    cols_mapping = {
        'pos_seq_num': 'posseqnum',
        'organization': 'posorgshortdesc',
        'position_number': 'posnumtext',
        'grade': 'posgradecode',
        'title': 'postitledesc',
        'languages': 'languages',
    }

    add_these.extend(hard_coded)

    return services.map_return_template_cols(add_these, cols_mapping, data)

def get_frequent_positions(query, jwt_token):
    '''
    Get all frequent positions
    '''
    args = {
        "uri": "classifications",
        "query": query,
        "query_mapping_function": None,
        "jwt_token": jwt_token,
        "mapping_function": fsbid_to_talentmap_frequent_positions,
        "count_function": None,
        "base_url": "/api/v1/positions/",
        "api_root": POSITIONS_ROOT,
    }

    frequentPositions = services.send_get_request(
        **args
    )

    return frequentPositions

def fsbid_to_talentmap_frequent_positions(data):
    data = data['position']
    position = data[0]

    # hard_coded are the default data points (opinionated EP)
    # add_these are the additional data points we want returned
    hard_coded = ['pos_seq_num', 'pos_org_short_desc', 'pos_num_text', 'pos_grade_code', 'pos_title_desc']
    add_these = []

    cols_mapping = {
        'pos_seq_num': 'posseqnum',
        'pos_org_short_desc': 'posorgshortdesc',
        'pos_num_text': 'posnumtext',
        'pos_grade_code': 'posgradecode',
        'pos_title_desc': 'postitledesc'
    }

    add_these.extend(hard_coded)

    return services.map_return_template_cols(add_these, cols_mapping, position)