import logging
from urllib.parse import urlencode, quote
from functools import partial
import pydash

import requests  # pylint: disable=unused-import

from django.conf import settings

import talentmap_api.fsbid.services.common as common
from talentmap_api.fsbid.views import reference as views

API_ROOT = settings.WS_ROOT_API_URL

logger = logging.getLogger(__name__)


def get_cycles(jwt_token):
    '''
    Gets bid cycles
    '''
    view = views.FSBidCyclesView
    uri = view.uri
    mapping_function = view.mapping_function 

    response = common.get_fsbid_results(
        uri,
        jwt_token,
        mapping_function,
        None,
        True,
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
def fsbid_tours_of_duty_to_talentmap_tours_of_duty(data):
    return {
        "code": data.get("todcode", 0),
        "is_active": True, # TODs returned from this call are not legacy
        "months": data.get("todmonthsnum", 0),
        "long_description": data.get("toddesctext", None),
        "short_description": data.get("todshortdesc", None)
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
    glossary_terms = {
        'T': 'Tandem',
        '8': '6 8 - Six Eight Year Rule',
        'A': 'AMB Ambassador',
        'F': 'Fair Share',
        'P': 'Pickering Fellow',
    }
    gloss_term = pydash.get(glossary_terms, pydash.get(data, "tp_code", None), None)
    return {
        "code": data.get("tp_code", None),
        "text": data.get("tp_descr_txt", None),
        "disabled_ind": data.get("disabled_ind", "N") == "Y",
        "id": data.get("te_id", None),
        "season_text": data.get("te_descr_txt", None),
        "glossary_term": gloss_term if gloss_term else pydash.get(data, "tp_descr_txt", None),
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

def get_travel_functions(query, jwt_token):
    '''
    Get agenda travel-functions
    '''
    args = {
        "uri": "v1/references/travel-functions",
        "query": query,
        "query_mapping_function": None,
        "jwt_token": jwt_token,
        "mapping_function": fsbid_to_talentmap_travel_functions,
        "count_function": None,
        "base_url": "/api/v1/",
        "api_root": API_ROOT,
    }

    travel_functions = common.send_get_request(
        **args
    )

    return travel_functions

def fsbid_to_talentmap_travel_functions(data):
    # hard_coded are the default data points (opinionated EP)
    # add_these are the additional data points we want returned

    hard_coded = ['code', 'desc_text', 'abbr_desc_text']

    add_these = []

    cols_mapping = {
        'code': 'tfcd',
        'desc_text': 'tfdescr',
        'abbr_desc_text': 'tfshortnm'
    }

    add_these.extend(hard_coded)

    return common.map_return_template_cols(add_these, cols_mapping, data)


def tmap_to_fsbid_gsa_location_query(query):
    '''
    Converts TalentMap filters into FSBid filters
    '''
    values = {
        # Pagination
        "rp.pageNum": int(query.get("page", 1)),
        "rp.pageRows": int(query.get("limit", 10)),
        "rp.columns": None,
        "rp.orderBy": ["locgvtstcntrydescr", "loccity", "locstate"],
        "rp.filter": common.convert_to_fsbid_ql([
            {"col": "locgvtgeoloccd", "val": query.get("code", None)},
            {"col": "loceffdt", "val": query.get("effective_date", None)},
            {"col": "loceffstatus", "val": query.get("status", None)},
            {"col": "locgvtstcntrydescr", "val": query.get("description", None)},
            {"col": "loccity", "val": query.get("city", None)},
            {"col": "locstate", "val": query.get("state", None)},
            {"col": "loccounty", "val": query.get("county", None)},
            {"col": "loccountry", "val": query.get("country", None)},
            {"col": "locgvtleopayarea", "val": query.get("pay_area", None)},
            {"col": "locgvtlocalityarea", "val": query.get("locality_area", None)},
        ]),
    }

    if query.get("getCount") == 'true':
        values["rp.pageNum"] = 0
        values["rp.pageRows"] = 0
        values["rp.columns"] = "ROWCOUNT"

    valuesToReturn = pydash.omit_by(values, lambda o: o is None or o == [])

    return urlencode(valuesToReturn, doseq=True, quote_via=quote)



def get_gsa_locations(query, jwt_token):
    '''
    Get gsa locations
    '''
    expected_keys = [
        "locgvtgeoloccd",
        "loceffdt",
        "loceffstatus",
        "locgvtstcntrydescr",
        "loccity",
		"locstate",
        "loccounty",
        "loccountry",
        "locgvtleopayarea",
        "locality_area",
    ]

    mapping_subset = pydash.pick(gsa_locations_cols_mapping, *expected_keys)

    args = {
        "uri": "v1/references/gsa-locations",
        "query": query,
        "query_mapping_function": tmap_to_fsbid_gsa_location_query,
        "jwt_token": jwt_token,
        "mapping_function": partial(common.map_fsbid_template_to_tm, mapping=mapping_subset),
        "count_function": get_gsa_locations_count,
        "base_url": "/api/v1/references/",
        "api_root": API_ROOT,
    }

    return common.send_get_request(**args)


def get_gsa_locations_count(query, jwt_token, host=None):
    '''
    Get total number of GSA locations
    '''
    args = {
        "uri": "v1/references/gsa-locations",
        "query": query,
        "query_mapping_function": tmap_to_fsbid_gsa_location_query,
        "jwt_token": jwt_token,
        "host": host,
        "api_root": API_ROOT,
        "use_post": False,
        "is_template": True,
    }
    return common.send_count_request(**args)


gsa_locations_cols_mapping = {
    "locgvtgeoloccd": "code",
    "loceffdt": "effective_date",
    "loceffstatus": "status",
    "locgvtstcntrydescr": "description",
    "loccity": "city",
    "locstate": "state", 
    "loccounty": "county", 
    "loccountry": "country", 
    "locgvtleopayarea": "pay_area", 
    "locgvtlocalityarea": "locality_area", 
}

