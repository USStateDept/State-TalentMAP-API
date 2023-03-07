import logging
from urllib.parse import urlencode, quote
from functools import partial
import pydash
import csv
import maya
import jwt
from copy import deepcopy
from django.http import HttpResponse
from datetime import datetime
from django.utils.encoding import smart_str

from django.conf import settings

from talentmap_api.fsbid.services import common as services

PANEL_API_ROOT = settings.PANEL_API_URL

logger = logging.getLogger(__name__)

panel_dates_mapping = {
    'pmdpmseqnum': 'pm_seq_num',
    'pmdmdtcode': 'mdt_code',
    'pmddttm': 'pmd_dttm',
    'mdtcode': 'mdt_code',
    'mdtdesctext': 'mdt_desc_text',
    'mdtordernum': 'mdt_order_num',
}

panel_cols_mapping = {
    'pmseqnum': 'pm_seq_num',
    'pmdpmseqnum': 'pm_seq_num',
    'pmddttm': 'pmd_dttm',
    'pmvirtualind': 'pm_virtual',
    'pmcreateid': 'pm_create_id',
    'pmcreatedate': 'pm_create_date',
    'pmupdateid': 'pm_update_id',
    'pmupdatedate': 'pm_update_date',
    'pmpmtcode': 'pmt_code',
    'pmtcode': 'pmt_code',
    'pmtdesctext': 'pmt_desc_text',
    'pmpmscode': 'pms_code',
    'pmscode': 'pms_code',
    'pmsdesctext': 'pms_desc_text',
    'miccode': 'mic_code',
    'micdesctext': 'mic_desc_text',
    'panelMeetingDates': {
        'nameMap': 'panelMeetingDates',
        'listMap': panel_dates_mapping,
    },
}


def get_panel_dates(query, jwt_token):
    '''
    Get panel dates
    '''
    expected_keys = ['pmdpmseqnum', 'pmddttm', 'pmpmtcode']

    mapping_subset = pydash.pick(panel_cols_mapping, *expected_keys)

    args = {
        "uri": "references/dates",
        "query": query,
        "query_mapping_function": convert_panel_dates_query,
        "jwt_token": jwt_token,
        "mapping_function": partial(services.map_fsbid_template_to_tm, mapping=mapping_subset),
        "count_function": None,
        "base_url": "/api/v1/panels/",
        "api_root": PANEL_API_ROOT,
    }

    return services.send_get_request(**args)

def convert_panel_dates_query(query):
    '''
    Converts TalentMap query into FSBid query
    '''

    values = {
        "rp.pageNum": int(query.get("page", 1)),
        "rp.pageRows": int(query.get("limit", 1000)),
        "rp.filter": services.convert_to_fsbid_ql([{'col': 'pmdmdtcode', 'val': 'MEET'}]),
    }

    valuesToReturn = pydash.omit_by(values, lambda o: o is None or o == [])

    return urlencode(valuesToReturn, doseq=True, quote_via=quote)


def get_panel_statuses(query, jwt_token):
    '''
    Get panel statuses
    '''
    mapping = {
        'pmscode': 'code',
        'pmsdesctext': 'text',
    }

    args = {
        "uri": "references/statuses",
        "query": query,
        "query_mapping_function": convert_panel_statuses_query,
        "jwt_token": jwt_token,
        "mapping_function": partial(services.map_fsbid_template_to_tm, mapping=mapping),
        "count_function": None,
        "base_url": "/api/v1/panels/",
        "api_root": PANEL_API_ROOT,
    }

    return services.send_get_request(**args)

def convert_panel_statuses_query(query):
    '''
    Converts TalentMap query into FSBid query
    '''

    values = {
        "rp.pageNum": int(query.get("page", 1)),
        "rp.pageRows": int(query.get("limit", 1000)),
    }

    valuesToReturn = pydash.omit_by(values, lambda o: o is None or o == [])

    return urlencode(valuesToReturn, doseq=True, quote_via=quote)


def get_panel_types(query, jwt_token):
    '''
    Get panel types
    '''
    mapping = {
        'pmtcode': 'code',
        'pmtdesctext': 'text',
    }

    args = {
        "uri": "references/types",
        "query": query,
        "query_mapping_function": convert_panel_types_query,
        "jwt_token": jwt_token,
        "mapping_function": partial(services.map_fsbid_template_to_tm, mapping=mapping),
        "count_function": None,
        "base_url": "/api/v1/panels/",
        "api_root": PANEL_API_ROOT,
    }

    return services.send_get_request(**args)

def convert_panel_types_query(query):
    '''
    Converts TalentMap query into FSBid query
    '''

    values = {
        "rp.pageNum": int(query.get("page", 1)),
        "rp.pageRows": int(query.get("limit", 1000)),
        "rp.filter": services.convert_to_fsbid_ql([{'col': 'pmpmtcode', 'val': query.get("type")}]),
    }

    valuesToReturn = pydash.omit_by(values, lambda o: o is None or o == [])

    return urlencode(valuesToReturn, doseq=True, quote_via=quote)


def get_panel_categories(query, jwt_token):
    '''
    Get panel categories
    '''

    expected_keys = ['miccode', 'micdesctext']

    mapping_subset = pydash.pick(panel_cols_mapping, *expected_keys)

    args = {
        "uri": "references/categories",
        "query": query,
        "query_mapping_function": convert_panel_category_query,
        "jwt_token": jwt_token,
        "mapping_function": partial(services.map_fsbid_template_to_tm, mapping=mapping_subset),
        "count_function": None,
        "base_url": "/api/v1/panels/",
        "api_root": PANEL_API_ROOT,
    }

    return services.send_get_request(**args)

def convert_panel_category_query(query):
    '''
    Converts TalentMap query into FSBid query
    '''

    values = {
        "rp.pageNum": int(query.get("page", 1)),
        "rp.pageRows": int(query.get("limit", 25)),
    }

    valuesToReturn = pydash.omit_by(values, lambda o: o is None or o == [])

    return urlencode(valuesToReturn, doseq=True, quote_via=quote)


def get_panel_meetings(query, jwt_token):
    '''
    Get panel meetings
    '''
    expected_keys = [
        'pmseqnum', 'pmvirtualind', 'pmcreateid', 'pmcreatedate',
        'pmupdateid', 'pmupdatedate', 'pmpmscode', 'pmpmtcode',
        'pmtdesctext', 'pmsdesctext', 'panelMeetingDates'
    ]

    mapping_subset = pydash.pick(panel_cols_mapping, *expected_keys)
    print('🦄🦄🦄🦄🦄🦄🦄🦄🦄🦄')
    print(query)
    print('🦄🦄🦄🦄🦄🦄🦄🦄🦄🦄')

    args = {
        "uri": "",
        "query": query,
        "query_mapping_function": convert_panel_query,
        "jwt_token": jwt_token,
        "mapping_function": partial(services.map_fsbid_template_to_tm, mapping=mapping_subset),
        "count_function": get_panel_meetings_count,
        "base_url": "/api/v1/panels/",
        "api_root": PANEL_API_ROOT,
    }

    return services.send_get_request(**args)


def get_panel_meetings_count(query, jwt_token, host=None, use_post=False):
    '''
    Get total number of panel meetings for panel meeting search
    '''
    args = {
        "uri": "",
        "query": query,
        "query_mapping_function": convert_panel_query,
        "jwt_token": jwt_token,
        "host": host,
        "use_post": use_post,
        "is_template": True,
        "api_root": PANEL_API_ROOT,
    }
    return services.send_count_request(**args)

def convert_panel_query(query={}):
    '''
    Converts TalentMap query into FSBid query
    '''

    panelDateStart = query.get("panel-date-start")
    panelDateEnd = query.get("panel-date-end")

    filters = [
            {'col': 'pmpmtcode', 'val': services.if_str_upper(query.get('type')), 'com': 'IN'},
            {'col': 'pmscode', 'val': services.if_str_upper(query.get('status')), 'com': 'IN'},
            {'col': 'pmseqnum', 'val': query.get('id')},
        ]

    try:
        if panelDateStart and panelDateEnd:
            startVal = maya.parse(panelDateStart).datetime().strftime("%Y-%m-%d")
            endVal = maya.parse(panelDateEnd).datetime().strftime("%Y-%m-%d")
            filters.append({"col": "ELSA", "com": "GTEQ", "val": startVal, "isDate": True})
            filters.append({"col": "ELSA", "com": "LTEQ", "val": endVal, "isDate": True})
    except:
        logger.info(f"Invalid date {panelDateStart} or {panelDateEnd} could not be parsed.")



    values = {
        'rp.pageNum': int(query.get('page', 1)),
        'rp.pageRows': int(query.get('limit', 1000)),
        'rp.orderBy': services.sorting_values(query.get('ordering', 'panel_date')),
        'rp.filter': services.convert_to_fsbid_ql(filters),
    }

    if query.get("getCount") == 'true':
        values["rp.pageNum"] = 0
        values["rp.pageRows"] = 0
        values["rp.columns"] = "ROWCOUNT"

    valuesToReturn = pydash.omit_by(values, lambda o: o is None or o == [])

    print('🥳🥳🥳🥳🥳🥳🥳🥳🥳🥳')
    print(valuesToReturn)
    print('🥳🥳🥳🥳🥳🥳🥳🥳🥳🥳')

    return urlencode(valuesToReturn, doseq=True, quote_via=quote)

def get_panel_meetings_csv(query, jwt_token, rl_cd, host=None):
    csvQuery = deepcopy(query)
    csvQuery['page'] = 1
    csvQuery['limit'] = 1000

    mapping_subset = {
        'default': 'None Listed',
        'wskeys': {
            'pmtdesctext': {},
            'pmsdesctext': {},
            'panelMeetingDates': {
                'transformFn': services.panel_process_dates_csv,
            },
        }
    }
    args = {
        "uri": "",
        "query": csvQuery,
        "query_mapping_function": convert_panel_query,
        "count_function": None,
        "jwt_token": jwt_token,
        "mapping_function": partial(services.csv_fsbid_template_to_tm, mapping=mapping_subset),
        "base_url": "/api/v1/panels/",
        "api_root": PANEL_API_ROOT,
        "host": host,
        "use_post": False,
    }

    data = services.send_get_request(**args)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f"attachment; filename=panel_meetings_{datetime.now().strftime('%Y_%m_%d_%H%M%S')}.csv"

    writer = csv.writer(response, csv.excel)
    response.write(u'\ufeff'.encode('utf8'))

    # write the headers
    writer.writerow([
        smart_str(u"Meeting Type"),
        smart_str(u"Meeting Status"),
        smart_str(u"Panel Meeting Date"),
        smart_str(u"Preliminary Cutoff"),
        smart_str(u"Addendum Cutoff"),
        smart_str(u"Preliminary Run Time"),
        smart_str(u"Addendum Run Time"),
        smart_str(u"Post Panel Started"),
        smart_str(u"Post Panel Run Time"),
        smart_str(u"Agenda Completed Time"),
    ])

    writer.writerows(data['results'])

    return response