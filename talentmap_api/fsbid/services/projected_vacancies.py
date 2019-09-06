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


def get_projected_vacancies(query, jwt_token, host=None):
    '''
    Gets projected vacancies from FSBid
    '''
    url = f"{API_ROOT}/futureVacancies?{convert_pv_query(query)}"
    response = requests.get(url, headers={'JWTAuthorization': jwt_token, 'Content-Type': 'application/json'}).json()

    projected_vacancies = map(fsbid_pv_to_talentmap_pv, response["Data"])
    return {
        **services.get_pagination(query, get_projected_vacancies_count(query, jwt_token)['count'], "/api/v1/fsbid/projected_vacancies/", host),
        "results": projected_vacancies
    }


def get_projected_vacancies_count(query, jwt_token, host=None):
    '''
    Gets the total number of PVs for a filterset
    '''
    url = f"{API_ROOT}/futureVacanciesCount?{convert_pv_query(query)}"
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


def fsbid_pv_to_talentmap_pv(pv):
    '''
    Converts the response projected vacancy from FSBid to a format more in line with the Talentmap position
    '''
    return {
        "id": pv["fv_seq_num"],
        "ted": ensure_date(pv["ted"], utc_offset=-5),
        "bidcycle": {
            "id": pv["bsn_id"],
            "name": pv["bsn_descr_text"],
            "cycle_start_date": "",
            "cycle_deadline_date": "",
            "cycle_end_date": "",
            "active": True
        },
        "position": {

            "grade": pv["pos_grade_code"],
            "skill": pv["pos_skill_desc"],
            "bureau": pv["bureau_desc"],
            "organization": pv["post_org_country_state"],
            "tour_of_duty": pv["tod"],
            "languages": list(filter(None, [
                parseLanguage(pv["lang1"]),
                parseLanguage(pv["lang2"]),
            ])),
            "post": {
                "tour_of_duty": pv["tod"],
                "differential_rate": pv["bt_differential_rate_num"],
                "danger_pay": pv["bt_danger_pay_num"],
                "location": {
                    "id": 7,
                    "country": "",
                    "code": "",
                    "city": "",
                    "state": ""
                }
            },
            "current_assignment": {
                "user": pv["incumbent"],
                "estimated_end_date": ensure_date(pv["ted"], utc_offset=-5)
            },
            "position_number": pv["position"],
            "title": pv["pos_title_desc"],
            "availability": {
                "availability": True,
                "reason": ""
            },
            "bid_cycle_statuses": [
                {
                    "id": pv["fv_seq_num"],
                    "bidcycle": pv["bsn_descr_text"],
                    "position": pv["pos_title_desc"],
                    "status_code": "",
                    "status": ""
                }
            ],
            "latest_bidcycle": {
                "id": pv["bsn_id"],
                "name": pv["bsn_descr_text"],
                "cycle_start_date": "",
                "cycle_deadline_date": "",
                "cycle_end_date": "",
                "active": True
            },
            "description": {
                "content": pv["ppos_capsule_descr_txt"]
            }
        }
    }


def post_values(query):
    '''
    Handles mapping locations and groups of locations to FSBid expected params
    '''
    results = []
    if query.get("position__post__in"):
        post_ids = query.get("position__post__in").split(",")
        location_codes = Post.objects.filter(id__in=post_ids).values_list("_location_code", flat=True)
        results = results + list(location_codes)
    if len(results) > 0:
        return results


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
        return results

def overseas_values(query):
    if query.get("is_domestic") == "true":
        return "D"
    if query.get("is_domestic") == "false":
        return "O"

sort_dict = {
    "position__title": "pos_title_desc",
    "position__grade": "pos_grade_code",
    "position__bureau": "bureau_desc",
    "ted": "ted",
    "position__position_number": "position"
}

def sorting_values(sort):
    if sort is not None:
        return sort_dict.get(sort, None)

def convert_pv_query(query):
    '''
    Converts TalentMap filters into FSBid filters

    The TalentMap filters align with the position search filter naming
    '''
    values = {
        "fv_request_params.order_by": sorting_values(query.get("ordering", None)),
        "fv_request_params.page_index": int(query.get("page", 1)),
        "fv_request_params.page_size": query.get("limit", 25),
        "fv_request_params.freeText": query.get("q", None),
        "fv_request_params.bid_seasons": services.convert_multi_value(query.get("is_available_in_bidseason")),
        "fv_request_params.bureaus": bureau_values(query),
        "fv_request_params.overseas_ind": overseas_values(query),
        "fv_request_params.danger_pays": services.convert_multi_value(query.get("position__post__danger_pay__in")),
        "fv_request_params.grades": services.convert_multi_value(query.get("position__grade__code__in")),
        "fv_request_params.languages": services.convert_multi_value(query.get("language_codes")),
        "fv_request_params.differential_pays": services.convert_multi_value(query.get("position__post__differential_rate__in")),
        "fv_request_params.skills": services.convert_multi_value(query.get("position__skill__code__in")),
        "fv_request_params.tod_codes": services.convert_multi_value(query.get("position__post__tour_of_duty__code__in")),
        "fv_request_params.location_codes": post_values(query),
        "fv_request_params.pos_numbers": services.convert_multi_value(query.get("position__position_number__in", None)),
        "fv_request_params.seq_nums": services.convert_multi_value(query.get("id", None)),
    }
    return urlencode({i: j for i, j in values.items() if j is not None}, doseq=True)
