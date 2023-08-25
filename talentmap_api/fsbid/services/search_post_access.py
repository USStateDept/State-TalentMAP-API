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
        "mapping_function": None,
        "count_function": None,
        "base_url": "",
        "host": None,
        "api_root": WS_ROOT
    }
    spa_req = services.send_get_request(
        **args
    )
    spa_data = pydash.get(spa_req, 'results')

    return spa_data


def spa_filter_query_mapping(query):
    values = {
      "jsonInput": {},
      "procName": 'prc_lst_bureau_org_tree',
      "packageName": 'PKG_WEBAPI_WRAP_SPRINT99',
    }
    return urlencode(values, doseq=True, quote_via=quote)


# def fsbid_spa_to_tm_data_mapping(data):
    # bureau = pydash.get(data, 'PQRY_BUREAU_LEVEL_O') or None
    # country = pydash.get(data, 'PQRY_COUNTRY_O') or None
    # org = pydash.get(data, 'PQRY_ORG_LEVEL_O') or None
    # person = pydash.get(data, 'PQRY_PERSON_LEVEL_O') or None
    # position = pydash.get(data, 'PQRY_POSITION_LEVEL_O') or None

    # return {
    #     "bureau": bureau,
    #     "country": country,
    #     "org": org,
    #     "person": person,
    #     "position": position
    # }
