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
        for x in query['rmrkInsertionList']:
            formattedInsert = {}
            formattedInsert['ritext'] = x
            formattedInsert['ricreateid'] = hru_id
            formattedInsert['riupdateid'] = hru_id
            formattedInsert['rirolerestrictedind'] = 'N'
            formattedInsert['rirmrkseqnum'] = rmrk_seq_num
            create_remark_insert(rmrk_seq_num, formattedInsert, jwt_token)
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


def convert_remark_query(query, is_edit=False):
    '''
    Converts TalentMap Remarks into FSBid Remarks
    '''
    formatted_query = {
        'rmrkseqnum': query.get('rmrkseqnum'),
        'rmrkrccode': query.get('rmrkCategory'),
        'rmrkordernum': 0,
        'rmrkshortdesctext': query.get('shortDescription'),
        'rmrkmutuallyexclusiveind': 'N',
        'rmrktext': query.get('longDescription'),
        'rmrkactiveind': query.get('rmrkactiveind'),
        'rmrkcreateid': query.get('rmrkcreateid'),
        'rmrkcreatedate': query.get('rmrkcreatedate'),
        'rmrkupdateid': query.get('rmrkupdateid'),
        # Need to format the date for fsbid service, expects space b/w date and time, not T
        'rmrkupdatedate': query.get('rmrkupdatedate', '').replace('T', ' '),
    }
    if is_edit:
        del formatted_query['rmrkcreatedate']
    return formatted_query


def convert_remark_insert_query(query):
    '''
    Converts TalentMap Remark Inserts into FSBid Remark Inserts
    '''
    return {
        'riseqnum': query.get('riseqnum'),
        'rirmrkseqnum': query.get('rirmrkseqnum'),
        'riinsertiontext': query.get('ritext'),
        'rirolerestrictedind': query.get('rirolerestrictedind'),
        'ricreateid': query.get('ricreateid'), 
        'ricreatedate': query.get('ricreatedate'), 
        'riupdateid': query.get('riupdateid'),
        'riupdatedate': query.get('riupdatedate'),
    }


def edit_remark(query, jwt_token, host=None):
    '''
    Edit Remark
    '''
    hru_id = jwt.decode(jwt_token, verify=False).get('sub')
    query['rmrkupdateid'] = hru_id
    update_date = query['rmrkupdatedate'] 
    # format update date
    query['rmrkupdatedate'] = update_date
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

