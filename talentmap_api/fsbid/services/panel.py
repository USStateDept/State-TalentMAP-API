import logging
import pydash
import maya
from urllib.parse import urlencode, quote
from functools import partial
from copy import deepcopy
import pydash

from django.conf import settings

from django.conf import settings
from talentmap_api.fsbid.services import common as services
from django.core.exceptions import PermissionDenied

PANEL_API_ROOT = settings.PANEL_API_URL

logger = logging.getLogger(__name__)


def get_panel_dates(query, jwt_token):
    '''
    Get panel dates
    '''
    args = {
        "uri": "references/dates",
        "query": query,
        "query_mapping_function": convert_panel_query,
        "jwt_token": jwt_token,
        "mapping_function": fsbid_to_talentmap_panel,
        "count_function": None,
        "base_url": "/api/v1/panels/",
        "api_root": PANEL_API_ROOT,
    }

    panel = services.send_get_request(
        **args
    )

    return panel


def convert_panel_query(query):
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


def fsbid_to_talentmap_panel(data):
    # hard_coded are the default data points (opinionated EP)
    # add_these are the additional data points we want returned

    hard_coded = ['pm_seq_num', 'pmd_dttm', 'pmt_code']

    add_these = []

    cols_mapping = {
        'pm_seq_num': 'pmdpmseqnum',
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
        'pmt_code': 'pmpmtcode',
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

    add_these.extend(hard_coded)

    return services.map_return_template_cols(add_these, cols_mapping, data)

def get_panel_categories(query, jwt_token):
    '''
    Get panel categories
    '''
    args = {
        "uri": "references/categories",
        "query": query,
        "query_mapping_function": convert_panel_category_query,
        "jwt_token": jwt_token,
        "mapping_function": fsbid_to_talentmap_panel_categories,
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


def fsbid_to_talentmap_panel_categories(data):
    # hard_coded are the default data points (opinionated EP)
    # add_these are the additional data points we want returned

    hard_coded = ['mic_code', 'mic_desc_text', 'pmt_code']

    add_these = []

    cols_mapping = {
        'mic_code': 'miccode',
        'mic_desc_text': 'micdesctext',
    }

    add_these.extend(hard_coded)

    return services.map_return_template_cols(add_these, cols_mapping, data)
