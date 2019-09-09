import requests
import re
import logging

from urllib.parse import urlencode

from django.conf import settings
from django.db.models import Q

from talentmap_api.common.common_helpers import ensure_date
from talentmap_api.organization.models import Post, Organization, OrganizationGroup
import talentmap_api.fsbid.services.common as services

API_ROOT = settings.FSBID_API_URL

logger = logging.getLogger(__name__)


def get_available_positions(query, jwt_token, host=None):
    '''
    Gets available positions from FSBid
    '''
    url = f"{API_ROOT}/availablePositions?{convert_ap_query(query)}"
    response = requests.get(url, headers={'JWTAuthorization': jwt_token, 'Content-Type': 'application/json'}).json()

    available_positions = map(fsbid_ap_to_talentmap_ap, response["Data"])
    return {
        **services.get_pagination(query, get_available_positions_count(query, jwt_token)['count'], "/api/v1/fsbid/available_positions/", host),
        "results": available_positions
    }


def get_available_positions_count(query, jwt_token, host=None):
    '''
    Gets the total number of available positions for a filterset
    '''
    url = f"{API_ROOT}/availablePositionsCount?{convert_ap_query(query)}"
    response = requests.get(url, headers={'JWTAuthorization': jwt_token, 'Content-Type': 'application/json'}).json()
    return {"count": response["Data"][0]["count(1)"]}


# Pattern for extracting language parts from a string. Ex. "Spanish (3/3)"
LANG_PATTERN = re.compile("(.*?)\(.*\)\s(\d)/(\d)")


def parseLanguage(lang):
    '''
    Parses a language string from FSBid and turns it into what we want
    The lang param comes in as something like "Spanish (3/3)"
    '''
    if lang:
        match = LANG_PATTERN.search(lang)
        if match:
            language = {}
            language["language"] = match.group(1)
            language["reading_proficiency"] = match.group(2)
            language["spoken_proficiency"] = match.group(3)
            language["representation"] = match.group(0).rstrip()
            return language


def fsbid_ap_to_talentmap_ap(ap):
    '''
    Converts the response available position from FSBid to a format more in line with the Talentmap position
    '''
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
        "is_urgent_vacancy": "",
        "is_volunteer": "",
        "is_hard_to_fill": "",
        "position": {
            "id": "",
            "grade": ap["pos_grade_code"],
            "skill": ap["pos_skill_desc"],
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
            "is_highlighted": "",
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
                parseLanguage(ap["lang1"]),
                parseLanguage(ap["lang2"]),
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
        "bid_statistics": ""
    }


def post_values(query):
    '''
    Handles mapping locations and groups of locations to FSBid expected params
    '''
    results = []
    if query.get("is_domestic") == "true":
        domestic_codes = Post.objects.filter(location__country__code="USA").values_list("_location_code", flat=True)
        results = results + list(domestic_codes)
    if query.get("is_domestic") == "false":
        overseas_codes = Post.objects.exclude(location__country__code="USA").values_list("_location_code", flat=True)
        results = results + list(overseas_codes)
    if query.get("position__post__in"):
        post_ids = query.get("position__post__in").split(",")
        location_codes = Post.objects.filter(id__in=post_ids).values_list("_location_code", flat=True)
        results = results + list(location_codes)
    if len(results) > 0:
        return ",".join(results)


def bureau_values(query):
    '''
    Gets the ids for the functional/regional bureaus and maps to codes and their children
    '''
    results = []
    # functional bureau filter
    if query.get("org_has_groups"):
        func_bureaus = query.get("org_has_groups").split(",")
        func_org_codes = OrganizationGroup.objects.filter(id__in=func_bureaus).values_list("_org_codes", flat=True)
        # Flatten _org_codes
        func_bureau_codes = [item for sublist in func_org_codes for item in sublist]
        results = results + list(func_bureau_codes)
    # Regional bureau filter
    if query.get("position__bureau__code__in"):
        regional_bureaus = query.get("position__bureau__code__in").split(",")
        reg_org_codes = Organization.objects.filter(Q(code__in=regional_bureaus) | Q(_parent_organization_code__in=regional_bureaus)).values_list("code", flat=True)
        results = results + list(reg_org_codes)
    if len(results) > 0:
        return ",".join(results)


def convert_ap_query(query):
    '''
    Converts TalentMap filters into FSBid filters

    The TalentMap filters align with the position search filter naming
    '''
    values = {
        "request_params.page_index": int(query.get("page", 1)),
        "request_params.page_size": query.get("limit", 25),
        "request_params.freeText": query.get("q", None),
        "request_params.bid_seasons": query.get("is_available_in_bidseason"),
        "request_params.bureaus": bureau_values(query),
        "request_params.danger_pays": query.get("position__post__danger_pay__in"),
        "request_params.grades": query.get("position__grade__code__in"),
        "request_params.languages": query.get("language_codes"),
        "request_params.differential_pays": query.get("position__post__differential_rate__in"),
        "request_params.skills": query.get("position__skill__code__in"),
        "request_params.tod_codes": query.get("position__post__tour_of_duty__code__in"),
        "request_params.location_codes": post_values(query),
        "request_params.pos_numbers": query.get("position__position_number__in", None),
        "request_params.cp_ids": query.get("id", None),
    }
    return urlencode({i: j for i, j in values.items() if j is not None})
