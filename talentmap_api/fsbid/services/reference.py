import logging

import requests  # pylint: disable=unused-import

from django.conf import settings

import talentmap_api.fsbid.services.common as common
from talentmap_api.fsbid.views import reference as views

API_ROOT = settings.FSBID_API_URL

logger = logging.getLogger(__name__)


def get_cycles(jwt_token):
    '''
    Common function to get bid cycles
    '''
    view = views.FSBidCyclesView
    uri = view.uri
    mapping_function = view.mapping_function 

    response = common.get_fsbid_results(
        uri,
        jwt_token,
        mapping_function
    )
    return list(response)


@staticmethod
def fsbid_danger_pay_to_talentmap_danger_pay(data):
    return {
        "id": data.get("pay_percent_num", 0),
        "code": data.get("pay_percent_num", None),
        "description": data.get("pay_percentage_text", None)
    }


@staticmethod
def fsbid_cycles_to_talentmap_cycles(data):
    return {
        "id": data.get("cycle_id", 0),
        "name": data.get("cycle_name", None),
        "active": True,
        "cycle_deadline_date": None,
        "cycle_end_date": None,
        "cycle_start_date": None
    }


@staticmethod
def fsbid_bureaus_to_talentmap_bureaus(data):
    return {
        "bureau_organization": None,
        "code": data.get("bur", None),
        "groups": [],
        "highlighted_positions": [],
        "id": data.get("bur", 0),
        "is_bureau": True,
        "is_regional": data.get("isregional", None) == 1,
        "location": None,
        "long_description": data.get("bureau_long_desc", None),
        "parent_organization": None,
        "short_description": data.get("bureau_short_desc", None)
    }


@staticmethod
def fsbid_differential_rates_to_talentmap_differential_rates(data):
    return {
        "id": data.get("pay_percent_num", 0),
        "code": data.get("pay_percent_num", None),
        "description": data.get("pay_percentage_text", None)
    }


@staticmethod
def fsbid_grade_to_talentmap_grade(data):
    return {
        "id": data.get("grade_code", 0),
        "code": data.get("grade_code", None),
        "description": None
    }


@staticmethod
def fsbid_languages_to_talentmap_languages(data):
    return {
        "id": data.get("language_code", 0),
        "code": data.get("language_code", None),
        "formal_description": data.get("language_long_desc", None),
        "long_description": data.get("language_long_desc", None),
        "short_description": data.get("language_short_desc", None),
        "effective_date": None
    }


@staticmethod
def fsbid_tour_of_duties_to_talentmap_tour_of_duties(data):
    return {
        "id": data.get("code", 0),
        "code": data.get("code", 0),
        "is_active": True,
        "months": None,
        "long_description": data.get("long_desc", None),
        "short_description": data.get("long_desc", None)
    }


@staticmethod
def fsbid_codes_to_talentmap_codes(data):
    return {
        "id": data.get("jc_id", 0),
        "code": data.get("skl_code", 0),
        "cone": data.get("jc_nm_txt", None),
        "description": data.get("skill_descr", None)
    }


@staticmethod
def fsbid_codes_to_talentmap_cones(data):
    return {
        "id": data.get("jc_id", 0),
        "code": data.get("skl_code", 0),
        "category": data.get("jc_nm_txt", None),
        "description": data.get("skill_descr", None)
    }


@staticmethod
def fsbid_locations_to_talentmap_locations(data):
    return {
        "code": data.get("location_code", 0),
        "city": data.get("location_city", None),
        "state": data.get("location_state", None),
        "country": data.get("location_country", None),
        "is_domestic": data.get("is_domestic", None) == 1,
    }


@staticmethod
def fsbid_classifications_to_talentmap_classifications(data):
    return {
        "code": data.get("tp_code", None),
        "text": data.get("tp_descr_txt", None),
        "disabled_ind": data.get("disabled_ind", "N") == "Y",
        "id": data.get("te_id", None),
        "season_text": data.get("te_descr_txt", None),
    }


@staticmethod
def fsbid_post_indicators_to_talentmap_indicators(data):
    return {
        "code": data.get("bt_column_name", None),
        "description": data.get("bt_column_desc", None)
    }


@staticmethod
def fsbid_us_to_talentmap_us(data):
    return {
        "code": data.get("us_code", None),
        "description": data.get("us_desc_text", None)
    }


@staticmethod
def fsbid_commuter_posts_to_talentmap_commuter_posts(data):
    return {
        "code": data.get("cpn_code", 0),
        "description": data.get("cpn_desc", None),
        "cpn_freq_desc": data.get("cpn_freq_desc", None),
    }
