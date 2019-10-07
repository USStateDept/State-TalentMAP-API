import requests
import logging

from datetime import datetime

from django.conf import settings

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
    return [fsbid_bid_to_talentmap_bid(bid) for bid in bids if bid['cyclePosition']['cp_id'] == int(position_id)] if position_id else map(fsbid_bid_to_talentmap_bid, bids)


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


def can_delete_bid(bidStatus, cycle):
    '''
    Draft bids and submitted bids in an active cycle can be deleted
    '''
    return bidStatus == Bid.Status.draft or (bidStatus == Bid.Status.submitted and cycle['status'] == 'A')


def fsbid_bid_to_talentmap_bid(data):
    bidStatus = get_bid_status(data['statusCode'], data['handshakeCode'])
    return {
        "id": "",
        "bidcycle": data['cycle']['description'],
        "emp_id": data['employee']['perdet_seq_num'],
        "user": "",
        "bid_statistics": [
            {
              "id": "",
              "bidcycle": data['cycle']['description'],
              "total_bids": data['cyclePosition']['totalBidders'],
              "in_grade": data['cyclePosition']['atGradeBidders'],
              "at_skill": data['cyclePosition']['inConeBidders'],
              "in_grade_at_skill": data['cyclePosition']['inBothBidders'],
              "has_handshake_offered": data['cyclePosition']['status'] == 'HS',
              "has_handshake_accepted": data['cyclePosition']['status'] == 'HS'
            }
        ],
        "position": {
            "id": data['cyclePosition']['pos_seq_num'],
            "position_number": data['cyclePosition']['pos_seq_num'],
            "status": data['cyclePosition']['status'],
            "grade": "",
            "skill": "",
            "bureau": "",
            "title": "",
            "create_date": data['submittedDate'],
            "update_date": "",
            "post": {
                "id": "",
                "location": {
                    "id": "",
                    "country": "",
                    "code": "",
                    "city": "",
                    "state": ""
                }
            }
        },
        "waivers": [],
        "can_delete": can_delete_bid(bidStatus, data['cycle']),
        "status": bidStatus,
        "draft_date": "",
        "submitted_date": datetime.strptime(data['submittedDate'], "%Y/%m/%d"),
        "handshake_offered_date": "",
        "handshake_accepted_date": "",
        "handshake_declined_date": "",
        "in_panel_date": "",
        "scheduled_panel_date": "",
        "approved_date": "",
        "declined_date": "",
        "closed_date": "",
        "is_priority": False,
        "panel_reschedule_count": 0,
        "create_date": datetime.strptime(data['submittedDate'], "%Y/%m/%d"),
        "update_date": "",
        "reviewer": ""
    }