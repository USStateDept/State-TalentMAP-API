import requests
import logging
import jwt
import json
import itertools

from datetime import datetime

from django.conf import settings

from django.utils.encoding import smart_str

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
    filteredBids = {}
    # Filter out any bids with a status of "D" (deleted)
    filteredBids['Data'] = [b for b in list(bids['Data']) if smart_str(b["bs_cd"]) != 'D']
    return [fsbid_bid_to_talentmap_bid(bid) for bid in filteredBids.get('Data', []) if bid.get('cp_id') == int(position_id)] if position_id else map(fsbid_bid_to_talentmap_bid, filteredBids.get('Data', []))

def get_user_bids_csv(employee_id, jwt_token, position_id=None):
    '''
    Export bids for a user to CSV
    '''
    data = user_bids(employee_id, jwt_token, position_id)

    response = services.get_bids_csv(list(data), "bids")

    logger.info(response)

    return response

def bid_on_position(employeeId, cyclePositionId, jwt_token):
    '''
    Adds a bid on a position
    '''
    ad_id = jwt.decode(jwt_token, verify=False).get('unique_name')
    url = f"{API_ROOT}/bids/?cp_id={cyclePositionId}&perdet_seq_num={employeeId}&ad_id={ad_id}"
    response = requests.post(url, data={}, headers={'JWTAuthorization': jwt_token, 'Content-Type': 'application/json'}, verify=False)  # nosec
    response.raise_for_status()
    return response

def submit_bid_on_position(employeeId, cyclePositionId, jwt_token):
    '''
    Submits a bid on a position
    '''
    ad_id = jwt.decode(jwt_token, verify=False).get('unique_name')
    url = f"{API_ROOT}/bids/?cp_id={cyclePositionId}&perdet_seq_num={employeeId}&ad_id={ad_id}"
    response = requests.put(url, data={}, headers={'JWTAuthorization': jwt_token, 'Content-Type': 'application/json'}, verify=False)  # nosec
    response.raise_for_status()
    return response

def remove_bid(employeeId, cyclePositionId, jwt_token):
    '''
    Removes a bid from the users bid list
    '''
    ad_id = jwt.decode(jwt_token, verify=False).get('unique_name')
    url = f"{API_ROOT}/bids?cp_id={cyclePositionId}&perdet_seq_num={employeeId}&ad_id={ad_id}"
    return requests.delete(url, headers={'JWTAuthorization': jwt_token, 'Content-Type': 'application/json'}, verify=False)  # nosec


def get_bid_status(statusCode, handshakeCode, assignmentCreateDate, panelMeetingStatus):
    '''
    Map the FSBid status code and handshake code to a TalentMap status
        statusCode - W → Draft

        statusCode - A → Submitted

        handShakeCode A → Handshake Accepted

        statusCode - P → Paneled

        statusCode - D → Deleted

        statusCode - C → Closed

        statusCode - U → Unavailable
    '''
    if assignmentCreateDate != None:
        return Bid.Status.approved
    if statusCode == 'C':
        return Bid.Status.closed
    if statusCode == 'U':
        return Bid.Status.closed
    if statusCode == 'P':
        return Bid.Status.in_panel
    if panelMeetingStatus != None:
        return Bid.Status.in_panel
    if statusCode == 'W':
        return Bid.Status.draft
    if statusCode == 'A':
        if handshakeCode == 'Y':
            return Bid.Status.handshake_accepted
        else:
            return Bid.Status.submitted


def can_delete_bid(bidStatus, cycleStatus):
    '''
    Draft bids and submitted bids in an active cycle can be deleted
    '''
    return bidStatus == Bid.Status.draft or (bidStatus == Bid.Status.submitted and cycleStatus == 'A')


def fsbid_bid_to_talentmap_bid(data):
    bidStatus = get_bid_status(data.get('bs_cd'), data.get('ubw_hndshk_offrd_flg'), data.get('assignment_date'), data.get('panel_meeting_status'))
    canDelete = True if data.get('delete_ind', 'Y') == 'Y' else False
    cpId = int(float(data.get('cp_id')))
    perdet = str(int(data.get('perdet_seq_num')))

    return {
        "id": f"{perdet}_{cpId}",
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
            "id": cpId,
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
        "can_delete": canDelete,
        "status": bidStatus,
        "panel_status": data.get('panel_meeting_status', ''),
        "draft_date": ensure_date(data.get('ubw_create_dt'), utc_offset=-5),
        "submitted_date": ensure_date(data.get('ubw_submit_dt'), utc_offset=-5),
        "handshake_offered_date": "",
        "handshake_accepted_date": ensure_date(data.get("ubw_hndshk_offrd_dt"), utc_offset=-5),
        "handshake_declined_date": "",
        "in_panel_date": ensure_date(data.get('panel_meeting_date'), utc_offset=-5),
        "scheduled_panel_date": ensure_date(data.get('panel_meeting_date'), utc_offset=-5),
        "approved_date": ensure_date(data.get('assignment_date'), utc_offset=-5),
        "declined_date": "",
        "closed_date": "",
        "is_priority": False,
        "panel_reschedule_count": 0,
        "create_date": ensure_date(data.get('ubw_create_dt'), utc_offset=-5),
        "update_date": "",
        "reviewer": ""
    }
