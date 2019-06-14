import requests
import logging

from datetime import datetime

from urllib.parse import urlencode

from django.conf import settings

from talentmap_api.bidding.models import Bid

logger = logging.getLogger(__name__)

API_ROOT = settings.FSBID_API_URL


def user_bids(employee_id, position_id=None):
    '''
    Get bids for a user on a position or all if no position
    '''
    bids = requests.get(f"{API_ROOT}/bids/?employeeId={employee_id}").json()
    return [fsbid_bid_to_talentmap_bid(bid) for bid in bids if bid['cyclePosition']['cp_id'] == int(position_id)] if position_id else map(fsbid_bid_to_talentmap_bid, bids)


def bid_on_position(userId, employeeId, cyclePositionId):
    '''
    Submits a bid on a position
    '''
    response = requests.post(f"{API_ROOT}/bids", data={"perdet_seq_num": employeeId, "cp_id": cyclePositionId, "userId": userId})
    response.raise_for_status()
    return response


def remove_bid(employeeId, cyclePositionId):
    '''
    Removes a bid from the users bid list
    '''
    return requests.delete(f"{API_ROOT}/bids?cp_id={cyclePositionId}&perdet_seq_num={employeeId}")


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
        return Bid.Status.approved
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


def get_projected_vacancies(query, host=None):
    '''
    Gets projected vacancies from FSBid
    '''
    response = requests.get(f"{API_ROOT}/projectedVacancies?{convert_pv_query(query)}").json()
    projected_vacancies = map(fsbid_pv_to_talentmap_pv, response["positions"])
    return {
       **get_pagination(query, response["pagination"]["count"], "/api/v1/fsbid/projected_vacancies/", host),
       "results": projected_vacancies
    }


def get_pagination(query, count, base_url, host=None, ):
    '''
    Figures out all the pagination
    '''
    page = int(query.get("page", 0))
    limit = int(query.get("limit", 25))
    next_query = query.copy()
    next_query.__setitem__("page", page + 1)
    prev_query = query.copy()
    prev_query.__setitem__("page", page - 1)
    previous_url = f"{host}{base_url}{prev_query.urlencode()}" if host and page > 1 else None
    next_url = f"{host}{base_url}{next_query.urlencode()}" if host and page * limit < count else None
    return {
        "count": count,
        "next": next_url,
        "previous": previous_url
    }


def convert_pv_query(query):
    '''
    Converts TalentMap filters into FSBid filters

    The TalentMap filters align with the position search filter naming
    '''
    values = {
        "bsn_id": query.get("is_available_in_bidseason"),
        "bureauCode": query.get("bureau__code__in"),
        "dangerPay": query.get("post__danger_pay__in"),
        "gradeCode": query.get("grade__code__in"),
        "languageCode": query.get("language_codes"),
        "postDifferential": query.get("post__differential_rate__in"),
        "skillCode": query.get("skill__code__in"),
        "tourOfDutyCode": query.get("post__tour_of_duty__code__in"),
        "limit": query.get("limit", None),
        "page": query.get("page", None),
        "organizationCode": query.get("post__in"),
        "positionNumber": query.get("position_number__in")
    }
    return urlencode({i: j for i, j in values.items() if j is not None})


def fsbid_pv_to_talentmap_pv(pv):
    '''
    Converts the response projected vacancy from FSBid to a format more in line with the Talentmap position
    '''
    return {
        "id": pv["pos_id"],
        "grade": pv["grade"],
        "skill": pv["skill"],
        "bureau": pv["bureau"],
        "organization": pv["organization"],
        "tour_of_duty": pv["tour_of_duty"],
        "languages": [
            {
                "language": pv["language1"],
                "reading_proficiency": pv["reading_proficiency_1"],
                "spoken_proficiency": pv["spoken_proficiency_1"],
                "representation": pv["language_representation_1"]
            }
        ],
        "post": {
            "tour_of_duty": pv["tour_of_duty"],
            "differential_rate": pv["differential_rate"],
            "danger_pay": pv["danger_pay"],
            "location": {
                "id": 7,
                "country": "United States",
                "code": "171670031",
                "city": "Chicago",
                "state": "IL"
            }
        },
        "current_assignment": {
            "user": pv["incumbent"],
            "estimated_end_date": datetime.strptime(pv["ted"], "%m/%Y")
        },
        "position_number": pv["position_number"],
        "title": pv["title"],
        "availability": {
            "availability": True,
            "reason": ""
        },
        "bid_cycle_statuses": [
            {
                "id": pv["pos_id"],
                "bidcycle": pv["bsn_descr_text"],
                "position": "[D0144910] SPECIAL AGENT (Chicago, IL)",
                "status_code": "OP",
                "status": "Open"
            }
        ],
        "bid_statistics": [
            {
                "id": pv["pos_id"],
                "bidcycle": pv["bsn_descr_text"],
                "total_bids": 0,
                "in_grade": 0,
                "at_skill": 0,
                "in_grade_at_skill": 0,
                "has_handshake_offered": False,
                "has_handshake_accepted": False
            }
        ],
        "latest_bidcycle": {
            "id": 1,
            "name": pv["bsn_descr_text"],
            "cycle_start_date": "2018-08-15T19:17:30.065379Z",
            "cycle_deadline_date": "2019-03-27T00:00:00Z",
            "cycle_end_date": "2019-05-16T00:00:00Z",
            "active": True
        }
    }


def get_bid_seasons(bsn_future_vacancy_ind):
    url = f"{API_ROOT}/bidSeasons?=bsn_future_vacancy_ind={bsn_future_vacancy_ind}" if bsn_future_vacancy_ind else f"{API_ROOT}/bidSeasons"
    bid_seasons = requests.get(f"{API_ROOT}/bidSeasons").json()
    return map(fsbid_bid_season_to_talentmap_bid_season, bid_seasons)


def fsbid_bid_season_to_talentmap_bid_season(bs):
    return {
        "id": bs["bsn_id"],
        "description": bs["bsn_descr_text"],
        "start_date": datetime.strptime(bs["bsn_start_date"], "%Y/%m/%d"),
        "end_date": datetime.strptime(bs["bsn_end_date"], "%Y/%m/%d"),
        "panel_cut_off_date": datetime.strptime(bs["bsn_panel_cutoff_date"], "%Y/%m/%d")
    }
