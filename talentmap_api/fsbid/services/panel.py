import logging
from urllib.parse import urlencode, quote
from functools import partial
import pydash

from django.conf import settings

from talentmap_api.fsbid.services import common as services

PANEL_API_ROOT = settings.PANEL_API_URL

logger = logging.getLogger(__name__)

def fsbid_to_talentmap_panel(data, default_data, add_these=[]):
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

    return services.map_return_template_cols(add_these, cols_mapping, data)


def get_panel_dates(query, jwt_token):
    '''
    Get panel dates
    '''

    hard_coded = ['pm_seq_num', 'pmd_dttm', 'pmt_code']

    args = {
        "uri": "references/dates",
        "query": query,
        "query_mapping_function": convert_panel_dates_query,
        "jwt_token": jwt_token,
        "mapping_function": partial(fsbid_to_talentmap_panel, default_data=hard_coded),
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

    hard_coded = ['pms_code', 'pms_desc_text']

    args = {
        "uri": "references/statuses",
        "query": query,
        "query_mapping_function": convert_panel_statuses_query,
        "jwt_token": jwt_token,
        "mapping_function": partial(fsbid_to_talentmap_panel, default_data=hard_coded),
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

    hard_coded = ['pmt_desc_text', 'pmt_code']

    args = {
        "uri": "references/types",
        "query": query,
        "query_mapping_function": convert_panel_types_query,
        "jwt_token": jwt_token,
        "mapping_function": partial(fsbid_to_talentmap_panel, default_data=hard_coded),
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
    }

    valuesToReturn = pydash.omit_by(values, lambda o: o is None or o == [])

    return urlencode(valuesToReturn, doseq=True, quote_via=quote)


def get_panel_categories(query, jwt_token):
    '''
    Get panel categories
    '''

    hard_coded = ['mic_code', 'mic_desc_text', 'pmt_code']

    args = {
        "uri": "references/categories",
        "query": query,
        "query_mapping_function": convert_panel_category_query,
        "jwt_token": jwt_token,
        "mapping_function": partial(fsbid_to_talentmap_panel, default_data=hard_coded),
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
        "rp.pageRows": int(query.get("limit", 1000)),
    }

    valuesToReturn = pydash.omit_by(values, lambda o: o is None or o == [])

    return urlencode(valuesToReturn, doseq=True, quote_via=quote)


def get_panel_meetings(query, jwt_token):
    '''
    Get panel meetings
    '''

    hard_coded = ['pm_seq_num', 'pm_virtual', 'pm_create_id', 'pm_create_date',
                    'pm_update_id', 'pm_update_date', 'pms_code', 'pmt_code',
                    'pmt_desc_text', 'pms_desc_text', 'panelMeetingDates' ]

    args = {
    "uri": "",
    "query": query,
    "query_mapping_function": convert_panel_category_query,
    "jwt_token": jwt_token,
    "mapping_function": partial(fsbid_to_talentmap_panel, default_data=hard_coded),
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

    #  from the ui it looks like the date will actually be a date range.

    values = {
        "rp.pageNum": int(query.get("page", 1)),
        "rp.pageRows": int(query.get("limit", 1000)),
        "rp.filter": services.convert_to_fsbid_ql([
            {'col': 'pmpmtcode', 'val': query.get("type", None)},
            {'col': 'pmddttm', 'val': query.get("date", None)},
            {'col': 'pmscode', 'val': query.get("status", None)}
        ]),
    }


    #             openapi.Parameter("page", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='A page number within the paginated result set.'),
    #             openapi.Parameter("limit", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Number of results to return per page.'),
    #             openapi.Parameter("type", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Panel meeting type.'),
    #             openapi.Parameter("date", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Date of the Panel meeting.'),
    #             openapi.Parameter("status", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Panel meeting status.'),
    #         ])

    valuesToReturn = pydash.omit_by(values, lambda o: o is None or o == [])

    return urlencode(valuesToReturn, doseq=True, quote_via=quote)
