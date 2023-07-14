import logging

import pydash

from django.conf import settings

from talentmap_api.fsbid.services import common as services

FAVORITES_LIMIT = settings.FAVORITES_LIMIT
PV_API_V2_URL = settings.PV_API_V2_URL

API_ROOT = settings.WS_ROOT_API_URL

logger = logging.getLogger(__name__)

def submit_create_remark(remark, jwt_token={}):
    url = f"{API_ROOT}/v1/admin_panels/"

    remark['mutuallyExclusive'] = "N"

    args = {
        "uri": url,
        "query": remark,
        "query_mapping_function": convert_panel_admin_remark_query,
        "jwt_token": jwt_token,
        "mapping_function": "",
    }

    return services.get_results_with_post(
        **args
    )

def convert_panel_admin_remark_query(query):
    '''
    Converts TalentMap query into FSBid query
    '''
    return {
        "TBD_WS_rmrkInsertionList":  pydash.get(query, 'rmrkInsertionList'),
        "TBD_WS_longDescription": pydash.get(query, 'longDescription'),
        "TBD_WS_activeIndicator": pydash.get(query, 'activeIndicator'),
        "TBD_WS_mutuallyExclusive": pydash.get(query, 'mutuallyExclusive') or "N",
    }
