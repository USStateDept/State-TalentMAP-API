import requests
import logging

from datetime import datetime

from django.conf import settings

from talentmap_api.common.common_helpers import ensure_date

from talentmap_api.bidding.models import Bid
import talentmap_api.fsbid.services.common as services

API_ROOT = settings.FSBID_API_URL

logger = logging.getLogger(__name__)

def user_bids(employee_id, jwt_token, position_id=None):
    '''
    Get bids for a user on a position or all if no position
    '''
    url = f"{API_ROOT}/bids/?perdet_seq_num={employee_id}"
    bids = requests.get(url, headers={'JWTAuthorization': jwt_token, 'Content-Type': 'application/json'}, verify=False).json()  # nosec
    return [fsbid_bid_to_talentmap_bid(bid) for bid in bids if bid.get('cp_id') == int(position_id)] if position_id else map(fsbid_bid_to_talentmap_bid, bids)


def bid_on_position(employeeId, cyclePositionId, jwt_token):
    '''
    Adds a bid on a position
    '''
    url = f"{API_ROOT}/bids/?cp_id={cyclePositionId}&perdet_seq_num={employeeId}"
    response = requests.post(url, data={}, headers={'JWTAuthorization': jwt_token, 'Content-Type': 'application/json'}, verify=False)  # nosec
    response.raise_for_status()
    return response

def submit_bid_on_position(employeeId, cyclePositionId, jwt_token):
    '''
    Submits a bid on a position
    '''
    url = f"{API_ROOT}/bids/?cp_id={cyclePositionId}&perdet_seq_num={employeeId}"
    response = requests.put(url, data={}, headers={'JWTAuthorization': jwt_token, 'Content-Type': 'application/json'}, verify=False)  # nosec
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
    if handshakeCode == 'Y':
        return Bid.Status.handshake_offered
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
    bidStatus = get_bid_status(data.get('bs_cd'), data.get('ubw_hndshk_offrd_flg'))
    return {
        "id": f"{data.get('perdet_seq_num')}_{data.get('cp_id')}",
        "bidcycle": data.get('cycle_nm_txt'),
        "emp_id": data.get('perdet_seq_num'),
        "user": "",
        "bid_statistics": [
            {
              "id": "",
              "bidcycle": data.get('cycle_nm_txt'),
              "total_bids": data.get('cp_ttl_bidder_qty'),
              "in_grade": data.get('cp_at_grd_qty'),
              "at_skill": data.get('cp_in_cone_qty'),
              "in_grade_at_skill": data.get('cp_at_grd_in_cone_qty'),
              "has_handshake_offered": data.get('ubw_hndshk_offrd_flg') == 'Y',
              "has_handshake_accepted": False
            }
        ],
        "position": {
            "id": data.get('cp_id'),
            "position_number": data.get('pos_num_text'),
            "status": "",
            "grade": data.get("pos_grade_code"),
            "skill": data.get("pos_skill_desc"),
            "bureau": "",
            "title": data.get("ptitle"),
            "create_date": ensure_date(data.get('ubw_create_dt'), utc_offset=-5),
            "update_date": "",
            "post": {
                "id": "",
                "location": {
                    "id": "",
                    "country": data.get("location_country"),
                    "code": "",
                    "city": data.get("location_city"),
                    "state": data.get("location_state"),
                }
            }
        },
        "waivers": [],
        "can_delete": data.get('delete_id', True),
        "status": bidStatus,
        "draft_date": ensure_date(data.get('ubw_create_dt'), utc_offset=-5),
        "submitted_date": ensure_date(data.get('ubw_submit_dt'), utc_offset=-5),
        "handshake_offered_date": data.get("ubw_hndshk_offrd_dt"),
        "handshake_accepted_date": "",
        "handshake_declined_date": "",
        "in_panel_date": "",
        "scheduled_panel_date": "",
        "approved_date": "",
        "declined_date": "",
        "closed_date": "",
        "is_priority": False,
        "panel_reschedule_count": 0,
        "create_date": ensure_date(data.get('ubw_create_dt'), utc_offset=-5),
        "update_date": "",
        "reviewer": ""
    }