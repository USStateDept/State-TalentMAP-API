import logging
import jwt
import pydash
import maya
from copy import deepcopy

from django.conf import settings
from functools import partial

from django.utils.encoding import smart_str

from talentmap_api.bidding.models import BidHandshakeCycle

from talentmap_api.common.common_helpers import ensure_date
from urllib.parse import urlencode, quote

from talentmap_api.bidding.models import Bid, BidHandshake
from talentmap_api.fsbid.requests import requests

import talentmap_api.bidding.services.bidhandshake as bh_services
import talentmap_api.fsbid.services.available_positions as ap_services

API_ROOT = settings.WS_ROOT_API_URL
BIDS_V2_ROOT = settings.BIDS_API_V2_URL

logger = logging.getLogger(__name__)

def user_bids(employee_id, jwt_token, position_id=None, query={}):
    '''
    Get bids for a user on a position or all if no position
    '''
    from talentmap_api.fsbid.services.common import sort_bids
    url = f"{API_ROOT}/v1/bids/?perdet_seq_num={employee_id}"
    ordering_query = query.get("ordering", None)
    bids = requests.get(url, headers={'JWTAuthorization': jwt_token, 'Content-Type': 'application/json'}).json()
    filteredBids = {}
    # Filter out any bids with a status of "D" (deleted)
    filteredBids['Data'] = [b for b in list(pydash.get(bids, 'Data') or []) if smart_str(b["bs_cd"]) != 'D']
    mappedBids = [fsbid_bid_to_talentmap_bid(bid, jwt_token) for bid in filteredBids.get('Data', []) if bid.get('cp_id') == int(position_id)] if position_id else map(lambda b: fsbid_bid_to_talentmap_bid(b, jwt_token), filteredBids.get('Data', []))
    mappedBids = sort_bids(bidlist=mappedBids, ordering_query=ordering_query)
    return map_bids_to_disable_handshake_if_accepted(mappedBids)

def get_user_bids_csv(employee_id, jwt_token, position_id=None, query={}):
    '''
    Export bids for a user to CSV
    '''
    from talentmap_api.fsbid.services.common import get_bids_csv
    data = user_bids(employee_id, jwt_token, position_id, query)

    response = get_bids_csv(list(data), "bids", jwt_token)

    return response


def bid_on_position(employeeId, cyclePositionId, jwt_token):
    '''
    Adds a bid on a position
    '''
    ad_id = jwt.decode(jwt_token, verify=False).get('unique_name')
    url = f"{API_ROOT}/v1/bids/?cp_id={cyclePositionId}&perdet_seq_num={employeeId}&ad_id={ad_id}"
    response = requests.post(url, data={}, headers={'JWTAuthorization': jwt_token, 'Content-Type': 'application/json'})
    response.raise_for_status()
    return response


def submit_bid_on_position(employeeId, cyclePositionId, jwt_token):
    '''
    Submits a bid on a position
    '''
    ad_id = jwt.decode(jwt_token, verify=False).get('unique_name')
    url = f"{API_ROOT}/v1/bids/?cp_id={cyclePositionId}&perdet_seq_num={employeeId}&ad_id={ad_id}"
    response = requests.put(url, data={}, headers={'JWTAuthorization': jwt_token, 'Content-Type': 'application/json'})
    response.raise_for_status()
    return response


def register_bid_on_position(employeeId, cyclePositionId, jwt_token):
    '''
    Registers a bid on a position
    '''
    ad_id = jwt.decode(jwt_token, verify=False).get('unique_name')
    url = f"{API_ROOT}/v1/bids/handshake/?cp_id={cyclePositionId}&perdet_seq_num={employeeId}&ad_id={ad_id}&hs_cd=HS"
    response = requests.patch(url, data={}, headers={'JWTAuthorization': jwt_token, 'Content-Type': 'application/json'})
    response.raise_for_status()
    return response


def unregister_bid_on_position(employeeId, cyclePositionId, jwt_token):
    '''
    Unregisters a bid on a position
    '''
    ad_id = jwt.decode(jwt_token, verify=False).get('unique_name')
    url = f"{API_ROOT}/v1/bids/handshake/?cp_id={cyclePositionId}&perdet_seq_num={employeeId}&ad_id={ad_id}"
    response = requests.patch(url, data={}, headers={'JWTAuthorization': jwt_token, 'Content-Type': 'application/json'})
    response.raise_for_status()
    return response


def remove_bid(employeeId, cyclePositionId, jwt_token):
    '''
    Removes a bid from the users bid list
    '''
    ad_id = jwt.decode(jwt_token, verify=False).get('unique_name')
    url = f"{API_ROOT}/v1/bids?cp_id={cyclePositionId}&perdet_seq_num={employeeId}&ad_id={ad_id}"
    return requests.delete(url, headers={'JWTAuthorization': jwt_token, 'Content-Type': 'application/json'})


def map_bids_to_disable_handshake_if_accepted(bids):
    # Accepting a handshake should be disabled if another handshake within the same bid cycle has already been accepted

    bidsClone = deepcopy(list(bids))

    # get the cp_id and related bid cycle id of accepted handshakes
    hasAcceptedHandshakeIds = pydash.chain(bidsClone).filter_(
        lambda x: pydash.get(x, 'handshake.bidder_hs_code') == 'handshake_accepted' and pydash.get(x, 'handshake.hs_status_code') != 'handshake_revoked'
    ).map(
        lambda x: { 'cp_id': pydash.get(x, 'position_info.id'), 'cycle_id': pydash.get(x, 'position_info.bidcycle.id') }
    ).value()

    bidsClone = pydash.map_(bidsClone, lambda x: {
            **x,
            'accept_handshake_disabled': True if pydash.find(hasAcceptedHandshakeIds, lambda y:
                y['cycle_id'] == pydash.get(x, 'position_info.bidcycle.id'))
                and not pydash.find(hasAcceptedHandshakeIds, lambda y: y['cp_id'] == pydash.get(x, 'position_info.id'))
                else False,
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
    positionInfo = ap_services.get_all_position(str(cpId), jwt_token) or {}
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
        "position_info": {
            "id": cpId, # even if we can't return positionInfo, we can at least return id
            **positionInfo,
        },
    }

    if showHandshakeData:
        data["handshake"] = {
            **bh_services.get_bidder_handshake_data(cpId, perdet, True),
        }

    return data

def get_bids(query, jwt_token, pk):
    '''
    Get bids
    '''
    from talentmap_api.fsbid.services.common import send_get_request

    args = {
        "uri": "",
        "query": query,
        "query_mapping_function": partial(convert_bids_query, pk),
        "jwt_token": jwt_token,
        "mapping_function": fsbid_to_talentmap_bids,
        "count_function": None,
        "base_url": "api/v1/bidding/",
        "api_root": BIDS_V2_ROOT,
    }

    bids = send_get_request(
        **args
    )

    return bids


def convert_bids_query(pk, query):
    '''
    Converts TalentMap query into FSBid query
    '''
    from talentmap_api.fsbid.services.common import convert_to_fsbid_ql

    values = {
        "rp.pageNum": int(query.get("page", 1)),
        "rp.pageRows": int(query.get("limit", 1000)),
        "rp.filter": convert_to_fsbid_ql([{'col': 'ubwperdetseqnum', 'val': pk}, {'col': 'ubwhscode', 'val': 'HS'}]),
    }

    valuesToReturn = pydash.omit_by(values, lambda o: o is None or o == [])

    return urlencode(valuesToReturn, doseq=True, quote_via=quote)


def fsbid_to_talentmap_bids(data):
    # hard_coded are the default data points (opinionated EP)
    # add_these are the additional data points we want returned
    from talentmap_api.fsbid.services.common import map_return_template_cols, parseLanguagesToArr

    hard_coded = ['hs_code', 'cp_id', 'pos_seq_num', 'pos_num', 'pos_org_short_desc', 'pos_title', 'pos']

    add_these = []

    cols_mapping = {
        'hs_code': 'ubwhscode',
        'cp_id': 'ubwcpid',
        'pos_seq_num': 'cpposseqnum',
        'pos_num': 'posnumtext',
        'pos_org_short_desc': 'posorgshortdesc',
        'pos_title': 'postitledesc',
        'perdet': 'perdet_seq_num',
        'pos': 'position[0]',
    }

    add_these.extend(hard_coded)

    mappedKeys = map_return_template_cols(add_these, cols_mapping, data)
    mappedKeys['pos']['languages'] = parseLanguagesToArr(mappedKeys['pos'])

    return mappedKeys
