import logging
import jwt
import pydash

from django.conf import settings
from django.http import QueryDict
from django.http import HttpResponse
from django.utils.encoding import smart_str

from talentmap_api.fsbid.services import common as services

API_ROOT = settings.WS_ROOT_API_URL

logger = logging.getLogger(__name__)



def create_remark_and_remark_insert(query={}, jwt_token=None, host=None):
    '''
    Create remark and inserts
    '''
    hru_id = jwt.decode(jwt_token, verify=False).get('sub')
    query['rmrkcreateid'] = hru_id
    query['rmrkupdateid'] = hru_id
    query['rmrkactiveind'] = 'Y'
    remark = create_remark(query, jwt_token)
    rmrk_seq_num = pydash.get(remark, '[0].rmrk_seq_num')

    if rmrk_seq_num:
        if pydash.get(query, 'remarkInserts'):
            for x in query['remarkInserts']:
                x['ricreateid'] = hru_id
                x['riupdateid'] = hru_id
                x['rirolerestrictedind'] = 'N'
                x['rirmrkseqnum'] = rmrk_seq_num
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
    return {
        'rmrkseqnum': query.get('rmrkseqnum'),
        'rmrkrccode': query.get('rmrkrccode'),
        'rmrkordernum': query.get('rmrkordernum'),
        'rmrkshortdesctext': query.get('rmrkshortdesctext'),
        'rmrkmutuallyexclusiveind': query.get('rmrkmutuallyexclusiveind'),
        'rmrktext': query.get('rmrktext'),
        'rmrkactiveind': query.get('rmrkactiveind'),
        'rmrkcreateid': query.get('rmrkcreateid'),
        'rmrkcreatedate': query.get('rmrkcreatedate'),
        'rmrkupdateid': query.get('rmrkupdateid'),
        'rmrkupdatedate': query.get('rmrkupdatedate'),
    }

def convert_remark_insert_query(query):
    '''
    Converts TalentMap Remark Inserts into FSBid Remark Inserts
    '''
    return {
        'riseqnum': query.get('riseqnum'),
        'rirmrkseqnum': query.get('rirmrkseqnum'),
        'riinsertiontext': query.get('riinsertiontext'),
        'rirolerestrictedind': query.get('rirolerestrictedind'),
        'ricreateid': query.get('ricreateid'), 
        'ricreatedate': query.get('ricreatedate'), 
        'riupdateid': query.get('riupdateid'),
        'riupdatedate': query.get('riupdatedate'),
    }

def edit_remark_and_remark_insert(query={}, jwt_token=None, host=None):
    '''
    Edit remark and inserts
    '''
    hru_id = jwt.decode(jwt_token, verify=False).get('sub')
    remark = edit_remark(query, jwt_token)
    rmrk_seq_num = pydash.get(remark, '[0].rmrk_seq_num')

    if rmrk_seq_num:
        if pydash.get(query, 'remarkInserts'):
            query['rmrkseqnum'] = rmrk_seq_num
            for x in query['remarkInserts']:
                edit_remark_insert(x, query, jwt_token)
        else:
            logger.error("Create remark insert failed")
    else:
        logger.error("Create remark failed")


def edit_remark(query, jwt_token):
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

    return services.send_put_request(
        **args
    )


def edit_remark_insert(rmrk_seq_num, query, jwt_token):
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

    return services.send_put_request(
        **args
    )


