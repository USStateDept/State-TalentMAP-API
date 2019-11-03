import requests
import logging
import csv
from datetime import datetime

from urllib.parse import urlencode, quote

from django.conf import settings
from django.db.models import Q
from django.http import HttpResponse
from django.utils.encoding import smart_str
from django.core.exceptions import ObjectDoesNotExist

from talentmap_api.common.common_helpers import ensure_date, safe_navigation
from talentmap_api.bidding.models import BidCycle
from talentmap_api.available_positions.models import AvailablePositionDesignation
from talentmap_api.organization.models import Location

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
    designations = AvailablePositionDesignation.objects.filter(cp_id=ap.get("cp_id", None)).first()

    location = {}
    try:
        location = Location.objects.get(code=ap.get("pos_location_code", None))
    except ObjectDoesNotExist:
        logger.warning(f"No location with code {ap['pos_location_code']} was found.")

    return {
        "id": ap.get("cp_id", None),
        "status": None,
        "status_code": ap.get("cp_status", None),
        "ted": ensure_date(ap.get("ted", None), utc_offset=-5),
        "posted_date": ensure_date(ap.get("cp_post_dt", None), utc_offset=-5),
        "availability": {
            "availability": None,
            "reason": None
        },
        "is_urgent_vacancy": getattr(designations, 'is_urgent_vacancy', False),
        "is_volunteer": getattr(designations, 'is_volunteer', False),
        "is_hard_to_fill": getattr(designations, 'is_hard_to_fill', False),
        "position": {
            "id": None,
            "grade": ap.get("pos_grade_code", None),
            "skill": f"{ap.get('pos_skill_desc', None)} ({ap.get('pos_skill_code')})",
            "skill_code": ap.get("pos_skill_code", None),
            "bureau": ap.get("pos_bureau_short_desc", None),
            "organization": f"({ap.get('org_short_desc', None)}) {ap.get('org_long_desc', None)}",
            "tour_of_duty": ap.get("tod", None),
            "classifications": None,
            "representation": None,
            "availability": {
                "availability": None,
                "reason": None
            },
            "position_number": ap.get("position", None),
            "title": ap.get("pos_title_desc", None),
            "is_overseas": None,
            "is_highlighted": getattr(designations, 'is_highlighted', False),
            "create_date": None,
            "update_date": None,
            "effective_date": None,
            "posted_date": ensure_date(ap.get("cp_post_dt", None), utc_offset=-5),
            "description": {
                "id": None,
                "last_editing_user": None,
                "is_editable_by_user": None,
                "date_created": None,
                "date_updated": None,
                "content": ap.get("ppos_capsule_descr_txt", None),
                "point_of_contact": None,
                "website": None
            },
            "current_assignment": {
                "user": ap.get("incumbent", None),
                "tour_of_duty": ap.get("tod", None),
                "status": None,
                "start_date": None,
                "estimated_end_date": ensure_date(ap.get("ted", None), utc_offset=-5)
            },
            "post": {
                "id": None,
                "code": ap.get("pos_location_code", None),
                "tour_of_duty": ap.get("tod", None),
                "post_overview_url": None,
                "post_bidding_considerations_url": None,
                "cost_of_living_adjustment": None,
                "differential_rate": ap.get("bt_differential_rate_num", None),
                "danger_pay": ap.get("bt_danger_pay_num", None),
                "rest_relaxation_point": None,
                "has_consumable_allowance": None,
                "has_service_needs_differential": None,
                "obc_id": None,
                "location": {
                    "id": safe_navigation(location, 'id'),
                    "country": f"{safe_navigation(location, 'country')}",
                    "code": safe_navigation(location, 'code'),
                    "city": safe_navigation(location, 'city'),
                    "state": safe_navigation(location, 'state')
                }
            },
            "latest_bidcycle": {
                "id": ap.get("cycle_id", None),
                "name": ap.get("cycle_nm_txt", None),
                "cycle_start_date": None,
                "cycle_deadline_date": None,
                "cycle_end_date": None,
                "active": None
            },
            "languages": list(filter(None, [
                services.parseLanguage(ap.get("lang1", None)),
                services.parseLanguage(ap.get("lang2", None)),
            ])),
        },
        "bidcycle": {
            "id": ap.get("cycle_id", None),
            "name": ap.get("cycle_nm_txt", None),
            "cycle_start_date": None,
            "cycle_deadline_date": None,
            "cycle_end_date": None,
            "active": None
        },
        "bid_statistics": {
            "id": None,
            "total_bids": ap.get("cp_ttl_bidder_qty", None),
            "in_grade": ap.get("cp_at_grd_qty", None),
            "at_skill": ap.get("cp_in_cone_qty", None),
            "in_grade_at_skill": ap.get("cp_at_grd_in_cone_qty", None),
            "has_handshake_offered": None,
            "has_handshake_accepted": None
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
