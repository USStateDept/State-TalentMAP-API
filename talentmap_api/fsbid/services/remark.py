import csv
import logging
from functools import partial
from urllib.parse import urlencode, quote
from datetime import datetime
import jwt
import pydash

from django.conf import settings
from django.http import QueryDict
from django.http import HttpResponse
from django.utils.encoding import smart_str

from talentmap_api.fsbid.services import common as services
from talentmap_api.fsbid.services import client as client_services
import talentmap_api.fsbid.services.agenda_item_validator as ai_validator
from talentmap_api.common.common_helpers import ensure_date, sort_legs

AGENDA_API_ROOT = settings.AGENDA_API_URL
PANEL_API_ROOT = settings.PANEL_API_URL
CLIENTS_ROOT_V2 = settings.CLIENTS_API_V2_URL
API_ROOT = settings.WS_ROOT_API_URL

logger = logging.getLogger(__name__)



def create_remark_and_remark_insert(query={}, jwt_token=None, host=None):
    '''
    Create remark and inserts
    '''
    hru_id = jwt.decode(jwt_token, verify=False).get('sub')
    remark = create_remark(query, jwt_token)
    rmrk_seq_num = pydash.get(remark, '[0].rmrk_seq_num')

    if rmrk_seq_num:
        if pydash.get(query, 'remarkInserts'):
            query['rmrkseqnum'] = rmrk_seq_num
            for x in query['remarkInserts']:
                create_remark_insert(x, query, jwt_token)
        else:
            logger.error("Create remark insert failed")
    else:
        logger.error("Create remark failed")


def create_remark(query, jwt_token):
    '''
    Create Remark
    '''
    args = {
        "uri": "v1/remarks",
        "query": query,
        "query_mapping_function": convert_remark_query,
        "jwt_token": jwt_token,
        "mapping_function": "",
    }

    return services.get_results_with_post(
        **args
    )


def create_remark_insert(rmrk_seq_num, query, jwt_token):
    '''
    Create Remark Insert 
    '''
    args = {
        "uri": f"v1/remarks/{rmrk_seq_num}/inserts",
        "query": query,
        "query_mapping_function": convert_remark_insert_query,
        "jwt_token": jwt_token,
        "mapping_function": "",
    }

    return services.get_results_with_post(
        **args
    )


def convert_remark_query(query):
    '''
    Converts TalentMap Remarks into FSBid Remarks
    '''
    creator_id = pydash.get(query, "hru_id")
    return {
        'rmrkseqnum': query.get('rmrkseqnum'),
        'rmrkrccode': query.get('rmrkrccode'),
        'rmrkordernum': query.get('rmrkordernum'),
        'rmrkshortdesctext': query.get('rmrkshortdesctext'),
        'rmrkmutuallyexclusiveind': query.get('rmrkmutuallyexclusiveind'),
        'rmrktext': query.get('rmrktext'),
        'rmrkactiveind': query.get('rmrkactiveind'),
        'rmrkcreateid': creator_id,
        'rmrkcreatedate': query.get('rmrkcreatedate'),
        'rmrkupdateid': query.get('rmrkupdateid'),
        'rmrkupdatedate': query.get('rmrkupdatedate'),
    }

def convert_remark_insert_query(query):
    '''
    Converts TalentMap Remarks into FSBid Remarks
    '''
    creator_id = pydash.get(query, "hru_id")
    return {
        'riseqnum': query.get('riseqnum'),
        'rmrkseqnum': query.get('rmrkseqnum'),
        'riinsertiontext': query.get('riinsertiontext'),
        'rirolerestrictedind': query.get('rirolerestrictedind'),
        'ricreateid': creator_id, 
        'ricreatedate': query.get('ricreatedate'), 
        'riupdateid': query.get('riupdateid'),
        'riupdatedate': query.get('riupdatedate'),
    }

