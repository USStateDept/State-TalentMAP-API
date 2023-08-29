import pydash
from django.conf import settings
from urllib.parse import urlencode, quote
from talentmap_api.fsbid.services import common as services

WS_ROOT = settings.WS_ROOT_API_URL

def get_search_post_access_filters(jwt_token, request):
    '''
    Gets Filters for Search Post Access Page
    '''
    args = {
        "uri": "v1/backoffice/BackOfficeCRUD",
        "jwt_token": jwt_token,
        "query": request,
        "query_mapping_function": spa_filter_query_mapping,
        # "request_mapping_function": None,
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

def spa_filter_query_mapping(query):
    values = {
      "procName": 'prc_lst_bureau_org_tree',
      "packageName": 'PKG_WEBAPI_WRAP_SPRINT99',
    }
    return urlencode(values, doseq=True, quote_via=quote)

def fsbid_spa_to_tm_filter_data_mapping(data):
    # print('🐙🐙🐙🐙🐙🐙🐙🐙🐙🐙');
    # print('Mapping')
    # print('🐙🐙🐙🐙🐙🐙🐙🐙🐙🐙');
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



def get_search_post_access_data(jwt_token, request):
    print('🐙🐙🐙🐙🐙🐙🐙🐙🐙🐙');
    print('SAP Data Service')
    print(request)
    print('🐙🐙🐙🐙🐙🐙🐙🐙🐙🐙');
    '''
    Gets Data for Search Post Access Page
    '''
    mapped_request = map_search_post_access_request(request)
    print('🐙🐙🐙🐙🐙🐙🐙🐙🐙🐙');
    print('mapped request')
    print(mapped_request)
    print('🐙🐙🐙🐙🐙🐙🐙🐙🐙🐙');
    args = {
        "uri": "v1/backoffice/BackOfficeCRUD",
        "jwt_token": jwt_token,
        "query": request,
        "query_mapping_function": spa_data_query_mapping,
        # "request_mapping_function": None,
        # "count_function": None,
        # "base_url": "",
        # "host": None,
        "api_root": WS_ROOT,
        "json_body": mapped_request, 
    }
    spa_req = services.send_post_back_office(
        **args
    )
    # if len(spa_req['PQRY_ORG_ACCESS_O']) > 0:
    result = fsbid_to_tm_spa_data_mapping(spa_req)
    return result
    # else: 

def spa_data_query_mapping(query):
    values = {
      "procName": 'prc_lst_org_access',
      "packageName": 'PKG_WEBAPI_WRAP_SPRINT99',
    }
    return urlencode(values, doseq=True, quote_via=quote)

def fsbid_to_tm_spa_data_mapping(data):
    # print('🐙🐙🐙🐙🐙🐙🐙🐙🐙🐙');
    # print(data)
    # print('🐙🐙🐙🐙🐙🐙🐙🐙🐙🐙');
    table = data['PQRY_ORG_ACCESS_O']
    for item in table:
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

def map_search_post_access_request(req):
    mapped_request = {
      "PV_API_VERSION_I": "2",  
    }
    if req.get('roles'): mapped_request['PJSON_POST_ROLE_TAB_I'] = {
        "Data": {
        "ROLE_CODE": req['roles'],
      }        
    }
    if req.get('bureaus'): mapped_request['PJSON_BUREAU_TAB_I'] = {
        "Data": {
        "BUREAU_ORG_CODE": req['bureaus'],
      }        
    }
    if req.get('posts'): mapped_request['PJSON_POST_ROLE_TAB_I'] = {
        "Data": {
        "ROLE_CODE": req['posts'],
      }        
    }
    return mapped_request

# mapped_request = {
#     "PV_API_VERSION_I": "2",
#     "PJSON_POST_ROLE_TAB_I": {
#         "Data": {
#         "ROLE_CODE": "FSBid_Org_Bidders",
#       }
#     },
#     "PJSON_EMP_TAB_I": {
#       "Data": {
#         "PER_SEQ_NUM": "315463",
#       }
#     },
#       "PJSON_BUREAU_TAB_I": {
#         "Data": {
#           "BUREAU_ORG_CODE": "150000",
#           }
#         }
# }