import logging
from urllib.parse import urlencode, quote
from functools import partial
import pydash
import csv

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

    args = {
        "uri": "",
        "query": query,
        "query_mapping_function": convert_panel_query,
        "jwt_token": jwt_token,
        "mapping_function": partial(services.map_fsbid_template_to_tm, mapping=mapping_subset),
        "count_function": None,
        "base_url": "/api/v1/panels/",
        "api_root": PANEL_API_ROOT,
    }

    return services.send_get_request(**args)

def convert_panel_query(query={}):
    '''
    Converts TalentMap query into FSBid query
    '''

    values = {
        'rp.pageNum': int(query.get('page', 1)),
        'rp.pageRows': int(query.get('limit', 1000)),
        'rp.orderBy': services.sorting_values(query.get('ordering', 'meeting_status')),
        'rp.filter': services.convert_to_fsbid_ql([
            {'col': 'pmpmtcode', 'val': services.if_str_upper(query.get('type')), 'com': 'IN'},
            {'col': 'pmscode', 'val': services.if_str_upper(query.get('status')), 'com': 'IN'},
            {'col': 'pmseqnum', 'val': query.get('id')},
        ]),
    }

    valuesToReturn = pydash.omit_by(values, lambda o: o is None or o == [])

    return urlencode(valuesToReturn, doseq=True, quote_via=quote)

def get_panel_meetings_csv(query, jwt_token, rl_cd, host=None):
    print('hit services')
    from talentmap_api.fsbid.services.common import send_get_csv_request, mapBool
    from talentmap_api.fsbid.services.cdo import cdo
    ad_id = jwt.decode(jwt_token, verify=False).get('unique_name')
    try:
        cdos = list(cdo(jwt_token))
    except:
        cdos = []
    csvQuery = deepcopy(query)
    csvQuery['page'] = 1
    csvQuery['limit'] = 500
    args = {
        "uri": "",
        "query": csvQuery,
        "query_mapping_function": convert_panel_query,
        "jwt_token": jwt_token,
        "mapping_function": partial(services.map_fsbid_template_to_tm, mapping=mapping_subset),
        "base_url": PANEL_API_ROOT,
        "host": host,
        "use_post": False,
    }

    data = send_get_csv_request(**args)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f"attachment; filename=panel_meetings{datetime.now().strftime('%Y_%m_%d_%H%M%S')}.csv"

    writer = csv.writer(response, csv.excel)
    response.write(u'\ufeff'.encode('utf8'))

    # write the headers
    writer.writerow([
        smart_str(u"Name"),
        smart_str(u"Employee ID"),
        smart_str(u"CDO"),
        smart_str(u"Current Organization"),
        smart_str(u"TED"),
        smart_str(u"Has Handshake"),
        smart_str(u"Handshake Organization"),
        smart_str(u"Panel Meeting Date"),
        smart_str(u"Agenda Status"),
    ])

    for record in data:
        fallback = 'None listed'
        try:
            ted = smart_str(maya.parse(record["currentAssignment"]["TED"]).datetime().strftime('%m/%d/%Y'))
        except:
            ted = fallback
        try:
            panelMeetingDate = smart_str(maya.parse(record["agenda"]["panelDate"]).datetime().strftime('%m/%d/%Y'))
        except:
            panelMeetingDate = fallback
        
        hasHandshake = True if pydash.get(record, 'hsAssignment.orgDescription') else False
        
        writer.writerow([
            smart_str(pydash.get(record, 'person.fullName')),
            smart_str("=\"%s\"" % pydash.get(record, "person.employeeID")),
            smart_str(pydash.get(record, 'person.cdo.name') or fallback),
            smart_str(pydash.get(record, 'currentAssignment.orgDescription') or fallback),
            smart_str(ted),
            smart_str(mapBool[hasHandshake]),
            smart_str(pydash.get(record, 'hsAssignment.orgDescription') or fallback),
            smart_str(panelMeetingDate),
            smart_str(pydash.get(record, 'agenda.status') or fallback),
        ])
    return response