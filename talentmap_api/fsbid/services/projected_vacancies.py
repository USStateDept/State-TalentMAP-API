import requests
import logging
import csv
from datetime import datetime
import maya

from urllib.parse import urlencode, quote

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.utils.encoding import smart_str

from talentmap_api.common.common_helpers import ensure_date, safe_navigation
import talentmap_api.fsbid.services.common as services

API_ROOT = settings.FSBID_API_URL

logger = logging.getLogger(__name__)

def get_projected_vacancy(id, jwt_token):
    '''
    Gets an indivdual projected vacancy by id
    '''
    return services.get_individual(
        "futureVacancies",
        id,
        convert_pv_query,
        jwt_token,
        fsbid_pv_to_talentmap_pv
    )

def get_projected_vacancies(query, jwt_token, host=None):
    return services.send_get_request(
        "futureVacancies",
        query,
        convert_pv_query,
        jwt_token,
        fsbid_pv_to_talentmap_pv,
        get_projected_vacancies_count,
        "/api/v1/fsbid/projected_vacancies/",
        host
    )

def get_projected_vacancies_tandem(query, jwt_token, host=None):
    return services.send_get_request(
        "positions/futureVacancies/tandem",
        query,
        convert_pv_query,
        jwt_token,
        fsbid_pv_to_talentmap_pv,
        get_projected_vacancies_tandem_count,
        "/api/v1/fsbid/projected_vacancies/tandem/",
        host
    )

def get_projected_vacancies_count(query, jwt_token, host=None):
    '''
    Gets the total number of PVs for a filterset
    '''
    return services.send_count_request("futureVacanciesCount", query, convert_pv_query, jwt_token, host)

def get_projected_vacancies_tandem_count(query, jwt_token, host=None):
    '''
    Gets the total number of tandem PVs for a filterset
    '''
    return services.send_count_request("positions/futureVacancies/tandem", query, convert_pv_query, jwt_token, host)

def get_projected_vacancies_csv(query, jwt_token, host=None, limit=None, includeLimit=False):
    data = services.send_get_csv_request(
        "futureVacancies",
        query,
        convert_pv_query,
        jwt_token,
        fsbid_pv_to_talentmap_pv,
        "/api/v1/fsbid/projected_vacancies/",
        host,
        None,
        limit
    )

    count = get_projected_vacancies_count(query, jwt_token)
    response = services.get_ap_and_pv_csv(data, "projected_vacancies", False)

    if includeLimit is True and count['count'] > limit:
        response['Position-Limit'] = limit

    return response

def get_projected_vacancies_tandem_csv(query, jwt_token, host=None, limit=None, includeLimit=False):
    data = services.send_get_csv_request(
        "positions/futureVacancies/tandem",
        query,
        convert_pv_query,
        jwt_token,
        fsbid_pv_to_talentmap_pv,
        "/api/v1/fsbid/projected_vacancies/tandem/",
        host,
        None,
        limit
    )

    count = get_projected_vacancies_tandem_count(query, jwt_token)
    response = services.get_ap_and_pv_csv(data, "projected_vacancies", False, True)

    if includeLimit is True and count['count'] > limit:
        response['Position-Limit'] = limit

    return response


def fsbid_pv_to_talentmap_pv(pv):
    '''
    Converts the response projected vacancy from FSBid to a format more in line with the Talentmap position
    '''
    return {
        "id": pv.get("fv_seq_num", None),
        "ted": ensure_date(pv.get("ted", None), utc_offset=-5),
        "bidcycle": {
            "id": pv.get("bsn_id", None),
            "name": pv.get("bsn_descr_text", None),
            "cycle_start_date": None,
            "cycle_deadline_date": None,
            "cycle_end_date": None,
            "active": True
        },
        "tandem_nbr": pv.get("tandem_nbr", None), # Only appears in tandem searches
        "position": {
            "grade": pv.get("pos_grade_code", None),
            "skill": f"{pv.get('pos_skill_desc', None)} ({pv.get('pos_skill_code')})",
            "bureau": f"({pv.get('pos_bureau_short_desc', None)}) {pv.get('pos_bureau_long_desc', None)}",
            "skill": f"{pv.get('pos_skill_desc', None)} ({pv.get('pos_skill_code')})",
            "organization": f"({pv.get('org_short_desc', None)}) {pv.get('org_long_desc', None)}",
            "tour_of_duty": pv.get("tod", None),
            "languages": list(filter(None, [
                services.parseLanguage(pv.get("lang1", None)),
                services.parseLanguage(pv.get("lang2", None)),
            ])),
            "post": {
                "tour_of_duty": pv.get("tod", None),
                "post_overview_url": services.get_post_overview_url(pv.get("pos_location_code", None)),
                "post_bidding_considerations_url": services.get_post_bidding_considerations_url(pv.get("pos_location_code", None)),
                "obc_id": services.get_obc_id(pv.get("pos_location_code", None)),
                "differential_rate": pv.get("bt_differential_rate_num", None),
                "danger_pay": pv.get("bt_danger_pay_num", None),
                "location": {
                    "country": pv.get("location_country", None),
                    "code": pv.get("pos_location_code", None),
                    "city": pv.get("location_city", None),
                    "state": pv.get("location_state", None),
                },
            },
            "current_assignment": {
                "user": pv.get("incumbent", None),
                "estimated_end_date": ensure_date(pv.get("ted", None), utc_offset=-5)
            },
            "position_number": pv.get("position", None),
            "title": pv.get("pos_title_desc", None),
            "availability": {
                "availability": True,
                "reason": None
            },
            "bid_cycle_statuses": [
                {
                    "id": pv.get("fv_seq_num", None),
                    "bidcycle": pv.get("bsn_descr_text", None),
                    "position": pv.get("pos_title_desc", None),
                    "status_code": None,
                    "status": None
                }
            ],
            "latest_bidcycle": {
                "id": pv.get("bsn_id", None),
                "name": pv.get("bsn_descr_text", None),
                "cycle_start_date": None,
                "cycle_deadline_date": None,
                "cycle_end_date": None,
                "active": True
            },
            "description": {
                "content": pv.get("ppos_capsule_descr_txt", None),
                "date_updated": ensure_date(pv.get("ppos_capsule_modify_dt", None), utc_offset=5),
            }
        },
        "unaccompaniedStatus": pv.get("us_desc_text", None),
        "isConsumable": pv.get("bt_consumable_allowance_flg", None) == "Y",
        "isServiceNeedDifferential": pv.get("bt_service_needs_diff_flg", None) == "Y",
        "isDifficultToStaff": pv.get("bt_most_difficult_to_staff_flg", None) == "Y",
        "isEFMInside": pv.get("bt_inside_efm_employment_flg", None) == "Y",
        "isEFMOutside": pv.get("bt_outside_efm_employment_flg", None) == "Y",
    }

def convert_pv_query(query):
    '''
    Converts TalentMap filters into FSBid filters

    The TalentMap filters align with the position search filter naming
    '''
    values = {
        # Pagination
        "fv_request_params.order_by": services.sorting_values(query.get("ordering", None)),
        "fv_request_params.page_index": int(query.get("page", 1)),
        "fv_request_params.page_size": query.get("limit", 25),

        "fv_request_params.get_count": query.get("getCount", 'false'),

        # Tandem 1 filters
        "fv_request_params.seq_nums": services.convert_multi_value(query.get("id", None)),
        "fv_request_params.bid_seasons": services.convert_multi_value(query.get("is_available_in_bidseason")),
        "fv_request_params.overseas_ind": services.overseas_values(query),
        "fv_request_params.languages": services.convert_multi_value(query.get("language_codes")),
        "fv_request_params.bureaus": services.bureau_values(query),
        "fv_request_params.grades": services.convert_multi_value(query.get("position__grade__code__in")),
        "fv_request_params.location_codes": services.post_values(query),
        "fv_request_params.danger_pays": services.convert_multi_value(query.get("position__post__danger_pay__in")),
        "fv_request_params.differential_pays": services.convert_multi_value(query.get("position__post__differential_rate__in")),
        "fv_request_params.pos_numbers": services.convert_multi_value(query.get("position__position_number__in", None)),
        "fv_request_params.post_ind": services.convert_multi_value(query.get("position__post_indicator__in")),
        "fv_request_params.tod_codes": services.convert_multi_value(query.get("position__post__tour_of_duty__code__in")),
        "fv_request_params.skills": services.convert_multi_value(query.get("position__skill__code__in")),
        "fv_request_params.us_codes": services.convert_multi_value(query.get("position__us_codes__in")),
        "fv_request_params.freeText": query.get("q", None),

        # Common filters
        "fv_request_params.overseas_ind2": services.overseas_values(query),
        "fv_request_params.location_codes2": services.post_values(query),
        "fv_request_params.danger_pays2": services.convert_multi_value(query.get("position__post__danger_pay__in")),
        "fv_request_params.differential_pays2": services.convert_multi_value(query.get("position__post__differential_rate__in")),
        "fv_request_params.post_ind2": services.convert_multi_value(query.get("position__post_indicator__in")),
        "fv_request_params.us_codes2": services.convert_multi_value(query.get("position__us_codes__in")),
        "fv_request_params.freeText2": query.get("q", None),

        # Tandem 2 filters
        "fv_request_params.seq_nums2": services.convert_multi_value(query.get("id-tandem", None)),
        "fv_request_params.bid_seasons2": services.convert_multi_value(query.get("is_available_in_bidseason-tandem")),
        "fv_request_params.languages2": services.convert_multi_value(query.get("language_codes-tandem")),
        "fv_request_params.bureaus2": services.bureau_values(query, True),
        "fv_request_params.grades2": services.convert_multi_value(query.get("position__grade__code__in-tandem")),
        "fv_request_params.pos_numbers2": services.convert_multi_value(query.get("position__position_number__in-tandem", None)),
        "fv_request_params.tod_codes2": services.convert_multi_value(query.get("position__post__tour_of_duty__code__in-tandem")),
        "fv_request_params.skills2": services.convert_multi_value(query.get("position__skill__code__in-tandem")),
    }
    return urlencode({i: j for i, j in values.items() if j is not None}, doseq=True, quote_via=quote)