import logging
import pydash
from django.conf import settings
from urllib.parse import urlencode, quote
from talentmap_api.fsbid.services import common as services

logger = logging.getLogger(__name__)

WS_ROOT = settings.WS_ROOT_API_URL

# FILTERS

def get_search_post_access_filters(jwt_token, request):
    '''
    Gets Filters for Search Post Access Page
    '''
    args = {
        "uri": "v1/backoffice/BackOfficeCRUD",
        "jwt_token": jwt_token,
        "query": request,
        "query_mapping_function": search_post_access_query_mapping,
        "api_root": WS_ROOT,
        "json_body": {
          "PV_API_VERSION_I": '',
          "PV_AD_ID_I": '',
        }, 
    }
    spa_req = services.send_post_back_office(
        **args
    )
    result = fsbid_spa_to_tm_filter_data_mapping(spa_req)
    return result

def search_post_access_query_mapping(query):
    values = {
      "procName": 'prc_lst_bureau_org_tree',
      "packageName": 'PKG_WEBAPI_WRAP_SPRINT99',
    }
    return urlencode(values, doseq=True, quote_via=quote)

def fsbid_spa_to_tm_filter_data_mapping(data):
    bureau_filters = data['PQRY_BUREAU_LEVEL_O']
    for item in bureau_filters:
        for key, value in item.items():
            if key == 'Bureau':
                item['code'] = item.pop(key)
            elif key == 'ORG_SHORT_DESC':
                item['description'] = item.pop(key)

    org_filters = data['PQRY_ORG_LEVEL_O']
    for item in org_filters:
        for key, value in item.items():
            if key == 'Org':
                item['code'] = item.pop(key)
            elif key == 'ORG_DESC':
                item['description'] = item.pop(key)

    person_filters = data['PQRY_PERSON_LEVEL_O']
    for item in person_filters:
        for key, value in item.items():
            if key == 'PER_SEQ_NUM':
                item['code'] = item.pop(key)
            elif key == 'PER_FULL_NAME':
                item['description'] = item.pop(key)

    role_filters = data['PQRY_POST_ROLE_O']
    for item in role_filters:
        for key, value in item.items():
            if key == 'ROLE_CODE':
                item['code'] = item.pop(key)
            elif key == 'ROLE_DESC':
                item['description'] = item.pop(key)

    position_filters = data['PQRY_POSITION_LEVEL_O']
    for item in position_filters:
        for key, value in item.items():
            if key == 'POS_SKILL_CODE':
                item['code'] = item.pop(key)
            elif key == 'POS_SKILL_DESC':
                item['description'] = item.pop(key)

    location_filters = data['PQRY_COUNTRY_O']
    for item in location_filters:
        for key, value in item.items():
            if key == 'COUNTRY_STATE_CODE':
                item['code'] = item.pop(key)
            elif key == 'COUNTRY_STATE_DESC':
                item['description'] = item.pop(key)

    return {
        'bureauFilters': bureau_filters,
        'orgFilters': org_filters,
        'personFilters': person_filters,
        'roleFilters': role_filters,
        'positionFilters': position_filters,
        'locationFilters': location_filters,
    }


# GET DATA


def get_search_post_access_data(jwt_token, request):
    '''
    Gets Data for Search Post Access Page
    '''
    mapped_request = map_search_post_access_query(request)

    logger.info('🐙🐙🐙🐙🐙🐙🐙🐙🐙🐙');
    logger.info('spa GET request mapped request')
    logger.info(mapped_request)

    args = {
        "uri": "v1/backoffice/BackOfficeCRUD",
        "jwt_token": jwt_token,
        "query": request,
        "query_mapping_function": search_post_access_get_data_mapping,
        "api_root": WS_ROOT,
        "json_body": mapped_request,
    }
    spa_req = services.send_post_back_office(
        **args
    )
    # TODO add error handling here?
    result = fsbid_to_tm_spa_data_mapping(spa_req)
    return result

def search_post_access_get_data_mapping(query):
    values = {
      "procName": 'prc_lst_org_access',
      "packageName": 'PKG_WEBAPI_WRAP_SPRINT99',
    }
    return urlencode(values, doseq=True, quote_via=quote)

def fsbid_to_tm_spa_data_mapping(data):
    table = data['PQRY_ORG_ACCESS_O']

    half = len(table) // 2
    half_table = table[:half]

    # TODO - only return needed data
    for item in half_table:
        for key, value in item.items():
            if key == 'BUREAUNAME':
                item['bureau'] = item.pop(key)
            elif key == 'ORGNAME':
                item['post'] = item.pop(key)
            elif key == 'PERFULLNAME':
                item['employee'] = item.pop(key)
            elif key == 'BOAID':
                item['id'] = item.pop(key)
            elif key == 'BAT_DESCR_TXT':
                item['access_type'] = item.pop(key)
            elif key == 'ROLEDESCR':
                item['role'] = item.pop(key)
            elif key == 'POS_TITLE_DESC':
                item['title'] = item.pop(key)
            elif key == 'POS_SEQ_NUM':
                item['position'] = item.pop(key)
    return table


def format_request_data_to_string(request_values, table_key):
    data_entries = []
    for item in request_values:
        data_entry = f'"Data": {{"{table_key}": "{item}"}}'
        data_entries.append(data_entry)

    result_string = "{" + ",".join(data_entries) + "}"
    return result_string


def map_search_post_access_query(req):
    mapped_request = {
      "PV_API_VERSION_I": "2",  
    }
    if req.get('persons'):
        mapped_request['PJSON_EMP_TAB_I'] = format_request_data_to_string(req.get('persons'), 'PER_SEQ_NUM')
    if req.get('bureaus'):
        mapped_request['PJSON_BUREAU_TAB_I'] = format_request_data_to_string(req.get('bureaus'), 'BUREAU_ORG_CODE')
    if req.get('posts'):
        mapped_request['PJSON_COUNTRY_TAB_I'] = format_request_data_to_string(req.get('posts'), 'COUNTRY_STATE_CODE')
    if req.get('roles'):
        mapped_request['PJSON_POST_ROLE_TAB_I'] = format_request_data_to_string(req.get('roles'), 'ROLE_CODE')
    if req.get('orgs'):
        # TODO - orgs has a bug in FSBID and needs ORG_SHORT_DESC as well
        mapped_request['PJSON_ORG_TAB_I'] = format_request_data_to_string(req.get('orgs'), 'ORG_CODE')
    return mapped_request


# POST REQUEST


def remove_search_post_access(jwt_token, request):
    '''
    Remove Access for a Post
    '''
    mapped_request = map_search_post_access_post_request(request)

    logger.info('🐙🐙🐙🐙🐙🐙🐙🐙🐙🐙');
    logger.info('spa POST request mapped request')
    logger.info(mapped_request)

    args = {
        "uri": "v1/backoffice/BackOfficeCRUD",
        "jwt_token": jwt_token,
        "query": request,
        "query_mapping_function": remove_search_post_access_query_mapping,
        "api_root": WS_ROOT,
        "json_body": mapped_request, 
    }
    spa_req = services.send_post_back_office(
        **args
    )
    # TODO add error handling
    result = fsbid_to_tm_spa_data_mapping(spa_req)
    return result

def map_search_post_access_post_request(req):
    mapped_request = {
      "PV_API_VERSION_I": "2",  
    }
    
    mapped_request['PJSON_ORG_ACCESS_I'] = format_request_post_data_to_string(req.get('positions'), 'BOAID')
    return mapped_request

def format_request_post_data_to_string(request_values, table_key):
    data_entries = []
    for item in request_values:
        data_entry = f'"Data": {{"{table_key}": "{item}", "ACTION": "D"}}'
        data_entries.append(data_entry)

    result_string = "{" + ",".join(data_entries) + "}"
    return result_string

def remove_search_post_access_query_mapping(query):
    values = {
      "procName": 'prc_mod_org_access',
      "packageName": 'PKG_WEBAPI_WRAP_SPRINT99',
    }
    return urlencode(values, doseq=True, quote_via=quote)
