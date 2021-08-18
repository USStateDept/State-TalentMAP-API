import logging
import jwt
import requests
import pydash
import maya
from copy import deepcopy

from django.conf import settings

from django.utils.encoding import smart_str

from talentmap_api.bidding.models import BidHandshakeCycle

from talentmap_api.common.common_helpers import ensure_date

from talentmap_api.bidding.models import Bid, BidHandshake
import talentmap_api.fsbid.services.common as services
import talentmap_api.bidding.services.bidhandshake as bh_services
import talentmap_api.fsbid.services.available_positions as ap_services

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
    mappedBids = [fsbid_bid_to_talentmap_bid(bid, jwt_token) for bid in filteredBids.get('Data', []) if bid.get('cp_id') == int(position_id)] if position_id else map(lambda b: fsbid_bid_to_talentmap_bid(b, jwt_token), filteredBids.get('Data', []))
    return map_bids_to_disable_handshake_if_accepted(mappedBids)

def get_user_bids_csv(employee_id, jwt_token, position_id=None):
    '''
    Export bids for a user to CSV
    '''
    data = user_bids(employee_id, jwt_token, position_id)

    response = services.get_bids_csv(list(data), "bids", jwt_token)

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


def register_bid_on_position(employeeId, cyclePositionId, jwt_token):
    '''
    Registers a bid on a position
    '''
    ad_id = jwt.decode(jwt_token, verify=False).get('unique_name')
    url = f"{API_ROOT}/bids/handshake/?cp_id={cyclePositionId}&perdet_seq_num={employeeId}&ad_id={ad_id}&hs_cd=HS"
    response = requests.patch(url, data={}, headers={'JWTAuthorization': jwt_token, 'Content-Type': 'application/json'}, verify=False)  # nosec
    response.raise_for_status()
    return response


def unregister_bid_on_position(employeeId, cyclePositionId, jwt_token):
    '''
    Unregisters a bid on a position
    '''
    ad_id = jwt.decode(jwt_token, verify=False).get('unique_name')
    url = f"{API_ROOT}/bids/handshake/?cp_id={cyclePositionId}&perdet_seq_num={employeeId}&ad_id={ad_id}"
    response = requests.patch(url, data={}, headers={'JWTAuthorization': jwt_token, 'Content-Type': 'application/json'}, verify=False)  # nosec
    response.raise_for_status()
    return response


def remove_bid(employeeId, cyclePositionId, jwt_token):
    '''
    Removes a bid from the users bid list
    '''
    ad_id = jwt.decode(jwt_token, verify=False).get('unique_name')
    url = f"{API_ROOT}/bids?cp_id={cyclePositionId}&perdet_seq_num={employeeId}&ad_id={ad_id}"
    return requests.delete(url, headers={'JWTAuthorization': jwt_token, 'Content-Type': 'application/json'}, verify=False)  # nosec


def map_bids_to_disable_handshake_if_accepted(bids):
    bidsClone = deepcopy(list(bids))
    hasAcceptedHandshakeIds = pydash.chain(bidsClone).filter_(
        lambda x: pydash.get(x, 'handshake.bidder_hs_code') == 'handshake_accepted' and pydash.get(x, 'handshake.hs_status_code') != 'handshake_revoked'
    ).map('id').value()
    bidsClone = pydash.map_(bidsClone, lambda x: {
            **x,
            'accept_handshake_disabled': False if not hasAcceptedHandshakeIds else True if x['id'] not in hasAcceptedHandshakeIds else False
        })
    return bidsClone


def get_bid_status(statusCode, handshakeCode, assignmentCreateDate, panelMeetingStatus, handshakeAllowed):
    '''
    Map the FSBid status code and handshake code to a TalentMap status
        statusCode - W → Draft

        statusCode - A → Submitted

        handShakeCode Y, statusCode A → Handshake Accepted

        handshakeAllowed Y, statusCode A → Handshake Needs Registered

        statusCode - P → Paneled

        statusCode - D → Deleted

        statusCode - C → Closed

        statusCode - U → Unavailable
    '''
    if assignmentCreateDate is not None:
        return Bid.Status.approved
    if statusCode == 'C':
        return Bid.Status.closed
    if statusCode == 'U':
        return Bid.Status.closed
    if statusCode == 'P':
        return Bid.Status.in_panel
    if panelMeetingStatus is not None:
        return Bid.Status.in_panel
    if statusCode == 'W':
        return Bid.Status.draft
    if statusCode == 'A':
        if handshakeCode == 'Y':
            return Bid.Status.handshake_accepted
        # display register handshake (FSBid will only return this for CDOs)
        if handshakeAllowed == 'Y':
            return Bid.Status.handshake_needs_registered
        # null will just let the bidder know that it is submitted.
        # Similarly, handshakeAllowed == 'N' will let a CDO know that it is still pending review.
        else:
            return Bid.Status.submitted


def can_delete_bid(bidStatus, cycleStatus):
    '''
    Draft bids and submitted bids in an active cycle can be deleted
    '''
    return bidStatus == Bid.Status.draft or (bidStatus == Bid.Status.submitted and cycleStatus == 'A')


def fsbid_bid_to_talentmap_bid(data, jwt_token):
    bidStatus = get_bid_status(
        data.get('bs_cd'),
        data.get('ubw_hndshk_offrd_flg'),
        data.get('assignment_date'),
        data.get('panel_meeting_status'),
        data.get('handshake_allowed_ind')
    )
    canDelete = True if data.get('delete_ind', 'Y') == 'Y' else False
    cpId = int(data.get('cp_id'))
    perdet = str(int(float(data.get('perdet_seq_num'))))
    positionInfo = ap_services.get_available_position(str(cpId), jwt_token)
    cycle = pydash.get(positionInfo, 'bidcycle.id')

    showHandshakeData = True
    handshakeCycle = BidHandshakeCycle.objects.filter(cycle_id=cycle)
    if handshakeCycle:
        handshakeCycle = handshakeCycle.first()
        handshake_allowed_date = handshakeCycle.handshake_allowed_date
        if handshake_allowed_date and handshake_allowed_date > maya.now().datetime():
            showHandshakeData = False

    data = {
        "id": f"{perdet}_{cpId}",
        "emp_id": data.get('perdet_seq_num'),
        "user": "",
        "waivers": [],
        "can_delete": canDelete,
        "status": bidStatus,
        "panel_status": data.get('panel_meeting_status', ''),
        "draft_date": ensure_date(data.get('ubw_create_dt'), utc_offset=-5),
        "submitted_date": ensure_date(data.get('ubw_submit_dt'), utc_offset=-5),
        "handshake_accepted_date": ensure_date(data.get("ubw_hndshk_offrd_dt"), utc_offset=-5),
        "in_panel_date": ensure_date(data.get('panel_meeting_date'), utc_offset=-5),
        "scheduled_panel_date": ensure_date(data.get('panel_meeting_date'), utc_offset=-5),
        "approved_date": ensure_date(data.get('assignment_date'), utc_offset=-5),
        "declined_date": "",
        "closed_date": "",
        "is_priority": False,
        "panel_reschedule_count": 0,
        "create_date": ensure_date(data.get('ubw_create_dt'), utc_offset=-5),
        "update_date": "",
        "reviewer": "",
        "cdo_bid": data.get('cdo_bid') == 'Y',
        "position_info": positionInfo,
    }

    if showHandshakeData:
        data["handshake"] = {
            **bh_services.get_bidder_handshake_data(cpId, perdet),
        }

    return data
