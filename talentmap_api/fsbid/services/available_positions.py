import requests
import logging
import csv
from datetime import datetime

from urllib.parse import urlencode, quote

from django.conf import settings
from django.db.models import Q
from django.http import HttpResponse
from django.utils.encoding import smart_str

from talentmap_api.common.common_helpers import ensure_date
from talentmap_api.bidding.models import BidCycle
from talentmap_api.available_positions.models import AvailablePositionDesignation

import talentmap_api.fsbid.services.common as services

API_ROOT = settings.FSBID_API_URL

logger = logging.getLogger(__name__)


def get_available_position(id, jwt_token):
    '''
    Gets an indivdual available position by id
    '''
    return services.get_individual(
        "availablePositions",
        id,
        convert_ap_query,
        jwt_token,
        fsbid_ap_to_talentmap_ap
    )


def get_available_positions(query, jwt_token, host=None):
    '''
    Gets available positions
    '''
    return services.send_get_request(
        "availablePositions",
        query,
        convert_ap_query,
        jwt_token,
        fsbid_ap_to_talentmap_ap,
        get_available_positions_count,
        "/api/v1/fsbid/available_positions/",
        host
    )


def get_available_positions_count(query, jwt_token, host=None):
    '''
    Gets the total number of available positions for a filterset
    '''
    return services.send_count_request("availablePositionsCount", query, convert_ap_query, jwt_token, host)


def get_available_positions_csv(query, jwt_token, host=None):
    data = services.send_get_csv_request(
        "availablePositions",
        query,
        convert_ap_query,
        jwt_token,
        fsbid_ap_to_talentmap_ap,
        "/api/v1/fsbid/available_positions/",
        host
    )

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f"attachment; filename=available_positions_{datetime.now().strftime('%Y_%m_%d_%H%M%S')}.csv"

    writer = csv.writer(response, csv.excel)
    response.write(u'\ufeff'.encode('utf8'))

    # write the headers
    writer.writerow([
        smart_str(u"Position"),
        smart_str(u"Position Number"),
        smart_str(u"Skill"),
        smart_str(u"Grade"),
        smart_str(u"Bureau"),
        smart_str(u"Post City"),
        smart_str(u"Post Country"),
        smart_str(u"Tour of Duty"),
        smart_str(u"Languages"),
        smart_str(u"Service Needs Differential"),
        smart_str(u"Post Differential"),
        smart_str(u"Danger Pay"),
        smart_str(u"TED"),
        smart_str(u"Incumbent"),
        smart_str(u"Bid Cycle/Season"),
        smart_str(u"Posted Date"),
        smart_str(u"Status Code"),
    ])

    for record in data:
        writer.writerow([
            smart_str(record["position"]["title"]),
            smart_str("=\"%s\"" % record["position"]["position_number"]),
            smart_str(record["position"]["skill"]),
            smart_str("=\"%s\"" % record["position"]["grade"]),
            smart_str(record["position"]["bureau"]),
            smart_str(record["position"]["post"]["location"]["city"]),
            smart_str(record["position"]["post"]["location"]["country"]),
            smart_str(record["position"]["tour_of_duty"]),
            smart_str(record["position"]["languages"]).strip('[]'),
            smart_str(record["position"]["post"]["has_service_needs_differential"]),
            smart_str(record["position"]["post"]["differential_rate"]),
            smart_str(record["position"]["post"]["danger_pay"]),
            smart_str(record["ted"].strftime('%m/%d/%Y')),
            smart_str(record["position"]["current_assignment"]["user"]),
            smart_str(record["bidcycle"]["name"]),
            smart_str(record["posted_date"].strftime('%m/%d/%Y')),
            smart_str(record["status_code"]),
        ])
    return response

# Max number of similar positions to return
SIMILAR_LIMIT = 3

# Filters available positions by the criteria provides and by the position with the provided id
def filter_available_positions_exclude_self(id, criteria, jwt_token, host):
    return list(filter(lambda i: str(id) != str(i["id"]), get_available_positions({**criteria, **{"limit":SIMILAR_LIMIT}}, jwt_token, host)["results"]))

def get_similar_available_positions(id, jwt_token, host=None):
    '''
    Returns a query set of similar positions, using the base criteria.
    If there are not at least 3 results, the criteria is loosened.
    '''
    ap = get_available_position(id, jwt_token)
    base_criteria = {
        "position__post__code__in": ap["position"]["post"]["code"],
        "position__skill__code__in": ap["position"]['skill_code'],
        "position__grade__code__in": ap["position"]["grade"],
    }

    results = filter_available_positions_exclude_self(id, base_criteria, jwt_token, host)
    while len(results) < SIMILAR_LIMIT and len(base_criteria.keys()) > 0:
        del base_criteria[list(base_criteria.keys())[0]]
        results = filter_available_positions_exclude_self(id, base_criteria, jwt_token, host)

    return {"results": results}


def fsbid_ap_to_talentmap_ap(ap):
    '''
    Converts the response available position from FSBid to a format more in line with the Talentmap position
    '''
    designations = AvailablePositionDesignation.objects.filter(cp_id=ap["cp_id"]).first()
    return {
        "id": ap["cp_id"],
        "status": "",
        "status_code": ap["cp_status"],
        "ted": ensure_date(ap["ted"], utc_offset=-5),
        "posted_date": ensure_date(ap["cp_post_dt"], utc_offset=-5),
        "availability": {
            "availability": "",
            "reason": ""
        },
        "is_urgent_vacancy": getattr(designations, 'is_urgent_vacancy', False),
        "is_volunteer": getattr(designations, 'is_volunteer', False),
        "is_hard_to_fill": getattr(designations, 'is_hard_to_fill', False),
        "position": {
            "id": "",
            "grade": ap["pos_grade_code"],
            "skill": ap["pos_skill_desc"],
            "skill_code": ap["pos_skill_code"],
            "bureau": ap["pos_bureau_short_desc"],
            "organization": ap["post_org_country_state"],
            "tour_of_duty": ap["tod"],
            "classifications": "",
            "representation": "",
            "availability": {
                "availability": "",
                "reason": ""
            },
            "position_number": ap["position"],
            "title": ap["pos_title_desc"],
            "is_overseas": "",
            "is_highlighted": getattr(designations, 'is_highlighted', False),
            "create_date": "",
            "update_date": "",
            "effective_date": "",
            "posted_date": ensure_date(ap["cp_post_dt"], utc_offset=-5),
            "description": {
                "id": "",
                "last_editing_user": "",
                "is_editable_by_user": "",
                "date_created": "",
                "date_updated": "",
                "content": ap["ppos_capsule_descr_txt"],
                "point_of_contact": "",
                "website": ""
            },
            "current_assignment": {
                "user": ap["incumbent"],
                "tour_of_duty": ap["tod"],
                "status": "",
                "start_date": "",
                "estimated_end_date": ensure_date(ap["ted"], utc_offset=-5)
            },
            "post": {
                "id": "",
                "code": ap["pos_location_code"],
                "tour_of_duty": ap["tod"],
                "post_overview_url": "",
                "post_bidding_considerations_url": "",
                "cost_of_living_adjustment": "",
                "differential_rate": ap["bt_differential_rate_num"],
                "danger_pay": ap["bt_danger_pay_num"],
                "rest_relaxation_point": "",
                "has_consumable_allowance": "",
                "has_service_needs_differential": "",
                "obc_id": "",
                "location": {
                    "id": "",
                    "country": "",
                    "code": "",
                    "city": "",
                    "state": ""
                }
            },
            "latest_bidcycle": {
                "id": ap["cycle_id"],
                "name": ap["cycle_nm_txt"],
                "cycle_start_date": "",
                "cycle_deadline_date": "",
                "cycle_end_date": "",
                "active": ""
            },
            "languages": list(filter(None, [
                services.parseLanguage(ap["lang1"]),
                services.parseLanguage(ap["lang2"]),
            ])),
        },
        "bidcycle": {
            "id": ap["cycle_id"],
            "name": ap["cycle_nm_txt"],
            "cycle_start_date": "",
            "cycle_deadline_date": "",
            "cycle_end_date": "",
            "active": ""
        },
        "bid_statistics": {
            "id": "",
            "total_bids": ap["cp_ttl_bidder_qty"],
            "in_grade": ap["cp_at_grd_qty"],
            "at_skill": ap["cp_in_cone_qty"],
            "in_grade_at_skill": ap["cp_at_grd_in_cone_qty"],
            "has_handshake_offered": "",
            "has_handshake_accepted": ""
        }
    }

def bid_cycle_filter(cycle_ids):
    results = []
    if cycle_ids:
        ids = BidCycle.objects.filter(id__in=cycle_ids.split(",")).values_list("_id", flat=True)
        results = results + list(ids)
    if len(results) > 0:
        return results

def convert_ap_query(query):
    '''
    Converts TalentMap filters into FSBid filters

    The TalentMap filters align with the position search filter naming
    '''
    values = {
        "request_params.order_by": services.sorting_values(query.get("ordering", None)),
        "request_params.page_index": int(query.get("page", 1)),
        "request_params.page_size": query.get("limit", 25),
        "request_params.freeText": query.get("q", None),
        "request_params.cps_codes": services.convert_multi_value("OP,HS"),
        "request_params.assign_cycles": bid_cycle_filter(query.get("is_available_in_bidcycle")),
        "request_params.bureaus": services.bureau_values(query),
        "request_params.overseas_ind": services.overseas_values(query),
        "request_params.danger_pays": services.convert_multi_value(query.get("position__post__danger_pay__in")),
        "request_params.grades": services.convert_multi_value(query.get("position__grade__code__in")),
        "request_params.languages": services.convert_multi_value(query.get("language_codes")),
        "request_params.differential_pays": services.convert_multi_value(query.get("position__post__differential_rate__in")),
        "request_params.skills": services.convert_multi_value(query.get("position__skill__code__in")),
        "request_params.tod_codes": services.convert_multi_value(query.get("position__post__tour_of_duty__code__in")),
        "request_params.location_codes": services.post_values(query),
        "request_params.pos_numbers": services.convert_multi_value(query.get("position__position_number__in", None)),
        "request_params.cp_ids": services.convert_multi_value(query.get("id", None)),
    }
    return urlencode({i: j for i, j in values.items() if j is not None}, doseq=True, quote_via=quote)
