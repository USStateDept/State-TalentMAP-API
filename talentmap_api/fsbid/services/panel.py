import logging
from urllib.parse import urlencode, quote
from functools import partial
import pydash

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
    # flipped bc templates return lots of multiple value
    # so we'd want both pmdseqnum and pmseqnum to map
    # to pm_seq_num for TM
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


def fsbid_to_talentmap_panel(default_data, add_these=[]):
    # default_data: default data points (opinionated EP)
    # add_these: additional data points

    cols_mapping = {
        'pm_seq_num': 'pmdpmseqnum',
        # these can be multiple values - so we'd want pmdseqnum and pmseqnum to map
        # to pm_seq_num
        # pmt_code should go to pmpmtcode and pmtcode
        # check this assumption
        'pmd_dttm': 'pmddttm',
        'pm_virtual': 'pmvirtualind',
        'pm_create_id': 'pmcreateid',
        'pm_create_date': 'pmcreatedate',
        'pm_update_id': 'pmupdateid',
        'pm_update_date': 'pmupdatedate',
        'pmi_seq_num': 'pmiseqnum',
        'pmi_official_num': 'pmiofficialitemnum',
        'pmi_addendum': 'pmiaddendumind',
        'pmi_label_text': 'pmilabeltext',
        'pmi_create_id': 'pmicreateid',
        'pmi_create_date': 'pmicreatedate',
        'pmi_update_id': 'pmiupdateid',
        'pmi_update_date': 'pmiupdatedate',
        'pmt_code': 'pmtcode',
        'pmt_desc_text': 'pmtdesctext',
        'pmt_create_id': 'pmtcreateid',
        'pmt_create_date': 'pmtcreatedate',
        'pmt_update_id': 'pmtupdateid',
        'pmt_update_date': 'pmtupdatedate',
        'pms_code': 'pmscode',
        'pms_desc_text': 'pmsdesctext',
        'pms_create_id': 'pmscreateid',
        'pms_create_date': 'pmscreatedate',
        'pms_update_id': 'pmsupdateid',
        'pms_update_date': 'pmsupdatedate',
        'pmd_create_id': 'pmdcreateid',
        'pmd_create_date': 'pmdcreatedate',
        'pmd_update_id': 'pmdupdateid',
        'pmd_update_date': 'pmdupdatedate',
        'mdt_code': 'pmdmdtcode',
        'mdt_desc_text': 'mdtdesctext',
        'mdt_include_time': 'mdtincludetimeind',
        'mdt_user_input': 'mdtuserinputind',
        'mdt_create_id': 'mdtcreateid',
        'mdt_create_date': 'mdtcreatedate',
        'mdt_update_id': 'mdtupdateid',
        'mdt_update_date': 'mdtupdatedate',
        'mic_code': 'miccode',
        'mic_desc_text': 'micdesctext',
        'mic_virtual_ind': 'micvirtualallowedind',
        'mic_create_id': 'miccreateid',
        'mic_create_date': 'miccreatedate',
        'mic_update_id': 'micupdateid',
        'mic_update_date': 'micupdatedate',
    }

    add_these.extend(default_data)
    # print('🥹 🍭🍭🍭🍭🍭🍭🍭🍭🍭🍭 data', data)

    y = services.map_return_template_cols(add_these, cols_mapping)

    # print('4️⃣ 🍭🍭🍭🍭🍭🍭🍭🍭🍭🍭')
    # print(y)
    return y


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

    panel = services.send_get_request(
        **args
    )

    return panel


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

    expected_keys = ['pmscode', 'pmsdesctext']

    mapping_subset = pydash.pick(panel_cols_mapping, *expected_keys)

    args = {
        "uri": "references/statuses",
        "query": query,
        "query_mapping_function": convert_panel_statuses_query,
        "jwt_token": jwt_token,
        "mapping_function": partial(services.map_fsbid_template_to_tm, mapping=mapping_subset),
        "count_function": None,
        "base_url": "/api/v1/panels/",
        "api_root": PANEL_API_ROOT,
    }

    statuses = services.send_get_request(
        **args
    )

    return statuses


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

    expected_keys = ['pmtcode', 'pmtdesctext']

    mapping_subset = pydash.pick(panel_cols_mapping, *expected_keys)

    args = {
        "uri": "references/types",
        "query": query,
        "query_mapping_function": convert_panel_types_query,
        "jwt_token": jwt_token,
        "mapping_function": partial(services.map_fsbid_template_to_tm, mapping=mapping_subset),
        "count_function": None,
        "base_url": "/api/v1/panels/",
        "api_root": PANEL_API_ROOT,
    }

    types = services.send_get_request(
        **args
    )

    return types


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

    panel_cats = services.send_get_request(
        **args
    )
    return panel_cats


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
       'pmtdesctext', 'pmsdesctext', 'panelMeetingDates',
       'pmdpmseqnum', 'pmdmdtcode', 'pmddttm', 'mdtcode',
       'mdtdesctext', 'mdtordernum' ,
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

    panel_cats = services.send_get_request(
        **args
    )
    return panel_cats


def convert_panel_query(query):
    '''
    Converts TalentMap query into FSBid query
    '''

    values = {
        "rp.pageNum": int(query.get("page", 1)),
        "rp.pageRows": int(query.get("limit", 1000)),
        "rp.filter": services.convert_to_fsbid_ql([
            {'col': 'pmpmtcode', 'val': query.get("type", None).upper()},
            {'col': 'pmscode', 'val': query.get("status", None).upper()},
            {'col': 'pmseqnum', 'val': query.get("id", None)},
        ]),
    }

    valuesToReturn = pydash.omit_by(values, lambda o: o is None or o == [])

    return urlencode(valuesToReturn, doseq=True, quote_via=quote)
