import pydash
from django.conf import settings
from urllib.parse import urlencode, quote
from talentmap_api.fsbid.services import common as services

WS_ROOT = settings.WS_ROOT_API_URL

def get_search_post_access_filters(jwt_token, request):
    print('🐙🐙🐙🐙🐙🐙🐙🐙🐙🐙');
    print('Service')
    print('🐙🐙🐙🐙🐙🐙🐙🐙🐙🐙');
    '''
    Gets Filters for Search Post Access Page
    '''
  
    # req_body = {
    #   "json_input": {
    #     "PV_API_VERSION_I": '',
    #     "PV_AD_ID_I": '',
    #   },
    #   "procName": 'prc_lst_bureau_org_tree',
    #   "packageName": 'PKG_WEBAPI_WRAP_SPRINT99',    
    # }

    args = {
        "uri": "v1/backoffice/BackOfficeCRUD",
        "jwt_token": jwt_token,
        "query": request,
        "query_mapping_function": spa_filter_query_mapping,
        "mapping_function": None,
        # "count_function": None,
        # "base_url": "",
        # "host": None,
        "api_root": WS_ROOT,
        "json_body": {
          "PV_API_VERSION_I": '',
          "PV_AD_ID_I": '',
        }, 
    }
    spa_req = services.send_post_back_office(
        **args
    )
    return spa_req
    # spa_data = pydash.get(spa_req, 'results')
    # return spa_data

def spa_filter_query_mapping(query):
    values = {
      "procName": 'prc_lst_bureau_org_tree',
      "packageName": 'PKG_WEBAPI_WRAP_SPRINT99',
    }
    return urlencode(values, doseq=True, quote_via=quote)


# def fsbid_spa_to_tm_data_mapping(data):
#     print('🐙🐙🐙🐙🐙🐙🐙🐙🐙🐙');
#     print('Mapping')
#     print(data)
#     print('🐙🐙🐙🐙🐙🐙🐙🐙🐙🐙');
    # bureau = data.get('PQRY_BUREAU_LEVEL_O') or None
    # country = data.get('PQRY_COUNTRY_O') or None
    # org = data.get('PQRY_ORG_LEVEL_O') or None
    # person = data.get('PQRY_PERSON_LEVEL_O') or None
    # position = data.get('PQRY_POSITION_LEVEL_O') or None

    # return {
    #     "bureau": bureau,
    #     "country": country,
    #     "org": org,
    #     "person": person,
    #     "position": position
    # }
    # return data