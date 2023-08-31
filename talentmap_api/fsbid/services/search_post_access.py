import logging
import pydash
from copy import deepcopy
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
        "proc_name": 'prc_lst_bureau_org_tree',
        "package_name": 'PKG_WEBAPI_WRAP_SPRINT99',
        "api_root": WS_ROOT,
        "json_body": {
          "PV_API_VERSION_I": '',
          "PV_AD_ID_I": '',
        }, 
    }
    spa_req = services.send_post_back_office(
        **args
    )
    if spa_req is not None:
      result = fsbid_spa_to_tm_filter_data_mapping(spa_req)
      return result

def get_filter_data_from_response(data, data_map):
    filter_data = []
    for item in data:
        new_entry = {}
        for key, value in item.items():
            if key in data_map and (len(new_entry) != 2):
                new_entry[data_map[key]] = value
        filter_data.append(new_entry)
    return filter_data


def fsbid_spa_to_tm_filter_data_mapping(data):
    data_map = {
        'PER_SEQ_NUM': 'code',
        'PER_FULL_NAME': 'description',
        'Bureau': 'code',
        'ORG_SHORT_DESC': 'description',
        'ROLE_CODE': 'code',
        'ROLE_DESC': 'description',
        'POS_SKILL_CODE': 'code',
        'POS_SKILL_DESC': 'description',
        'COUNTRY_STATE_CODE': 'code',
        'COUNTRY_STATE_DESC': 'description',
    }

    return {
        'bureauFilters': get_filter_data_from_response(data['PQRY_BUREAU_LEVEL_O'], data_map),
        'personFilters': get_filter_data_from_response(data['PQRY_PERSON_LEVEL_O'], data_map),
        'roleFilters': get_filter_data_from_response(data['PQRY_POST_ROLE_O'], data_map),
        'positionFilters': get_filter_data_from_response(data['PQRY_POSITION_LEVEL_O'], data_map),
        'locationFilters': get_filter_data_from_response(data['PQRY_COUNTRY_O'], data_map),
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
        "proc_name": 'prc_lst_org_access',
        "package_name": 'PKG_WEBAPI_WRAP_SPRINT99',
        "api_root": WS_ROOT,
        "json_body": mapped_request,
    }
    spa_req = services.send_post_back_office(
        **args
    )
    if spa_req is not None:
      result = fsbid_to_tm_spa_data_mapping(spa_req)
      return result

def fsbid_to_tm_spa_data_mapping(data):
    data_table = data['PQRY_ORG_ACCESS_O']
    return_table = []

    for item in data_table:
        new_entry = {}
        for key, value in item.items():
            if key == 'BUREAUNAME':
                new_entry['bureau'] = value
            elif key == 'LOCATIONNAME':
                new_entry['post'] = value
            elif key == 'PERFULLNAME':
                new_entry['employee'] = value
            elif key == 'BOAID':
                new_entry['id'] = value
            elif key == 'BAT_DESCR_TXT':
                new_entry['access_type'] = value
            elif key == 'ROLEDESCR':
                new_entry['role'] = value
            elif key == 'POS_TITLE_DESC':
                new_entry['title'] = value
            elif key == 'POS_SEQ_NUM':
                new_entry['position'] = value
        return_table.append(new_entry)

    return return_table


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
    args = {
        "uri": "v1/backoffice/BackOfficeCRUD",
        "jwt_token": jwt_token,
        "query": request,
        "proc_name": 'prc_mod_org_access',
        "package_name": 'PKG_WEBAPI_WRAP_SPRINT99',
        "api_root": WS_ROOT,
        "json_body": mapped_request, 
    }
    spa_req = services.send_post_back_office(
        **args
    )
    if spa_req is not None:
      return spa_req

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

