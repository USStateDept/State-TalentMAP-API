import requests
import logging

from django.conf import settings

from talentmap_api.bidding.models import Bid
from talentmap_api.common.common_helpers import ensure_date
import talentmap_api.fsbid.services.common as services

API_ROOT = settings.FSBID_API_URL

logger = logging.getLogger(__name__)

def user_bids(employee_id, jwt_token, position_id=None):
    '''
    Get bids for a user on a position or all if no position
    '''
    url = f"{API_ROOT}/bids/?perdet_seq_num={employee_id}"
    bids = requests.get(url, headers={'JWTAuthorization': jwt_token, 'Content-Type': 'application/json'}, verify=False).json()  # nosec
    return [fsbid_bid_to_talentmap_bid(bid) for bid in bids if bid['cp_id'] == int(position_id)] if position_id else map(fsbid_bid_to_talentmap_bid, bids)


def bid_on_position(userId, jwt_token, employeeId, cyclePositionId):
    '''
    Submits a bid on a position
    '''
    url = f"{API_ROOT}/bids/"
    response = requests.post(url, data={"perdet_seq_num": employeeId, "cp_id": cyclePositionId, "userId": userId}, headers={'JWTAuthorization': jwt_token, 'Content-Type': 'application/json'}, verify=False)  # nosec
    response.raise_for_status()
    return response


def remove_bid(employeeId, cyclePositionId, jwt_token):
    '''
    Removes a bid from the users bid list
    '''
    url = f"{API_ROOT}/bids?cp_id={cyclePositionId}&perdet_seq_num={employeeId}"
    return requests.delete(url, headers={'JWTAuthorization': jwt_token, 'Content-Type': 'application/json'}, verify=False)  # nosec


def get_bid_status(statusCode, handshakeCode):
    '''
    Map the FSBid status code and handshake code to a TalentMap status
        statusCode - W → Draft

        statusCode - A → Submitted

        handShakeCode A → Handshake Accepted

        statusCode - P → Paneled

        statusCode - D → Deleted
    '''
    if handshakeCode == 'A':
        return Bid.Status.handshake_accepted
    if statusCode == 'C':
        return Bid.Status.closed
    if statusCode == 'P':
        return Bid.Status.in_panel
    if statusCode == 'W':
        return Bid.Status.draft
    if statusCode == 'A':
        return Bid.Status.submitted


def can_delete_bid(bidStatus, cycleStatus):
    '''
    Draft bids and submitted bids in an active cycle can be deleted
    '''
    return bidStatus == Bid.Status.draft or (bidStatus == Bid.Status.submitted and cycleStatus == 'A')


def fsbid_bid_to_talentmap_bid(data):
    bidStatus = get_bid_status(data['cs_cd'], data['hs_code'])
    id = f"{data['per_seq_num']}_${data['cp_id']}"
    available = data['bid_unavailable_ind'] is not 'N'
    return {
        "approved_date": "",
        "bidcycle": data['cycle_nm_txt'],
        "can_delete": can_delete_bid(bidStatus, data['bs_cd']),
        "closed_date": "",
        "create_date": "",
        "declined_date": "",
        "draft_date": "",
        "emp_id": data['per_seq_num'],
        "handshake_accepted_date": "",
        "handshake_declined_date": "",
        "handshake_offered_date": "",
        "id": id,
        "in_panel_date": "",
        "is_priority": False,
        "panel_reschedule_count": 0,
        "position": {
            "availability": {
                "availability": available,
                "reason": ""
            },
            "bid_statistics": [
                {
                "at_skill": data['bid_count'],
                "has_handshake_accepted": data['hs_code'] == 'A',
                "has_handshake_offered": data['ubw_hndshk_offrd_flg'] == 'Y',
                "id": f"{id}_bidstats",
                "bidcycle": data['cycle_nm_txt'],
                "in_grade": data['bid_count'],
                "in_grade_at_skill": data['bid_count'],
                "total_bids": data['bid_count'],
                }
            ],
            "bidcycle": {
                "active": True,
                "cycle_deadline_date": "",
                "cycle_end_date": "",
                "cycle_start_date": "",
                "id": "",
                "name": data["cycle_nm_txt"]
            },
            "created": "",
            "id": data['cp_id'],
            "is_hard_to_fill": (data["acp_hard_to_fill_ind"] is not 'N'),
            "is_urgent_vacancy": False,
            "is_volunteer": False,
            "position": {
                "availability": {
                    "availability": available,
                    "reason": ""
                },
                "bureau": f"{data['pos_bureau_code']}",
                "classifications": [],
                "create_date": "",
                "description": {
                    "content": "",
                    "date_created": "",
                    "date_updated": "",
                    "id": "",
                    "is_editable_by_user": False,
                    "last_editing_user": None,
                    "point_of_contact": None,
                    "website": None,
                },
                "effective_date": "",
                "grade": data["pos_grade_code"],
                "id": f"{data['cp_id']}_{data['pos_seq_num']}",
                "is_highlighted": False,
                "is_overseas": False,
                "languages": [
                    {
                        "id": "",
                        "language": "",
                        "reading_proficiency": "",
                        "representation": data["pos_lang_desc"],
                        "spoken_proficiency": ""
                    }
                ],
                "latest_bidcycle": None,
                "organization": data["pos_org_short_desc"],
                "position_number": data['pos_num_text'],
                "post": {
                    "code": data["pos_bureau_code"],
                    "cost_of_living_adjustment": 0,
                    "danger_pay": 0,
                    "differential_rate": 0,
                    "has_consumable_allowance": False,
                    "has_service_needs_differential": True,
                    "id": "",
                    "location": {
                        "city": "",
                        "code": "",
                        "country": "",
                        "id": "",
                        "state": ""
                    },
                    "obc_id": None,
                    "post_bidding_considerations_url": None,
                    "post_overview_url": None,
                    "rest_relaxation_point": "",
                    "tour_of_duty": "",
                },
                "posted_date": "",
                "representation": "",
                "skill": f"{data['pos_skill_desc']} ({data['pos_skill_code']})",
                "title": data["ptitle"],
                "tour_of_duty": None,
                "updated": ""
            },
            "posted_date": "",
            "status": bidStatus,
            "status_code": "",
            "ted": data["ted"],
            "updated": ""            
        },
        "reviewer": None,
        "scheduled_panel_date": "",
        "status": bidStatus,
        "submitted_date": ensure_date(data["ubw_submit_dt"], utc_offset=-5),
        "update_date": "",
        "user": "",
        "waivers": []
    }