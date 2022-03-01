import logging
import pydash
import maya
from urllib.parse import urlencode, quote
from functools import partial
from copy import deepcopy
import pydash

# import requests  # pylint: disable=unused-import
from django.conf import settings

from django.conf import settings
from talentmap_api.fsbid.services import common as services
from django.core.exceptions import PermissionDenied

PANEL_API_ROOT = settings.PANEL_API_URL

logger = logging.getLogger(__name__)


def get_panel_dates(query, jwt_token, host=None):
    '''
    Get panel dates
    '''
    args = {
        "uri": "references/dates",
        "query": query,
        "query_mapping_function": convert_panel_query,
        "jwt_token": jwt_token,
        "mapping_function": fsbid_panel_to_talentmap_panel,
        "count_function": None,
        "base_url": "/api/v1/panels/",
        "host": host,
        "use_post": False,
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
        "rp.pageRows": query.get("limit", 5),
        "rp.columns": query.get("columns", None),
        # "rp.filter": services.convert_to_fsbid_ql('pmdmdtcode', query.get("pmd-dateCode", None)),
    }

    # TODO: how are we handling multiple passes to rp.filters?
    # TODO: handle sending in columns - what to call them?

    # a filter: pmdmdtcode|EQ|MEET|
    # a col: pmdmdtcode

    valuesToReturn = pydash.omit_by(values, lambda o: o is None or o == [])

    return urlencode(valuesToReturn, doseq=True, quote_via=quote)


def fsbid_panel_to_talentmap_panel(data):
    param_cols = ["mdt_code", "pms_code"]
    # param_cols = query.get("columns", None)
    # going to need a new send_get_request

    defined_cols = {
        'pm_seq_num': 'pmdpmseqnum',
        'pmd_dttm': 'pmddttm',
    }

    additional_cols = {
        'pm_virtual': 'pm_virtual',
        'pm_create_id': 'pm_create_id',
        'pm_create_date': 'pm_create_date',
        'pm_update_id': 'pm_update_id',
        'pm_update_date': 'pm_update_date',
        'pmi_seq_num': 'pmi_seq_num',
        'pmi_official_num': 'pmi_official_num',
        'pmi_addendum': 'pmi_addendum',
        'pmi_label_text': 'pmi_label_text',
        'pmi_create_id': 'pmi_create_id',
        'pmi_create_date': 'pmi_create_date',
        'pmi_update_id': 'pmi_update_id',
        'pmi_update_date': 'pmi_update_date',
        'pmt_code': 'pmt_code',
        'pmt_desc_text': 'pmt_desc_text',
        'pmt_create_id': 'pmt_create_id',
        'pmt_create_date': 'pmt_create_date',
        'pmt_update_id': 'pmt_update_id',
        'pmt_update_date': 'pmt_update_date',
        'pms_code': 'pms_code',
        'pms_desc_text': 'pms_desc_text',
        'pms_create_id': 'pms_create_id',
        'pms_create_date': 'pms_create_date',
        'pms_update_id': 'pms_update_id',
        'pms_update_date': 'pms_update_date',
        'pmd_create_id': 'pmd_create_id',
        'pmd_create_date': 'pmd_create_date',
        'pmd_update_id': 'pmd_update_id',
        'pmd_update_date': 'pmd_update_date',
        'mdt_code': 'mdt_code',
        'mdt_desc_text': 'mdt_desc_text',
        'mdt_include_time': 'mdt_include_time',
        'mdt_user_input': 'mdt_user_input',
        'mdt_create_id': 'mdt_create_id',
        'mdt_create_date': 'mdt_create_date',
        'mdt_update_id': 'mdt_update_id',
        'mdt_update_date': 'mdt_update_date',
        'mic_code': 'mic_code',
        'mic_desc_text': 'mic_desc_text',
        'mic_virtual_ind': 'mic_virtual_ind',
        'mic_create_id': 'mic_create_id',
        'mic_create_date': 'mic_create_date',
        'mic_update_id': 'mic_update_id',
        'mic_update_date': 'mic_update_date'
    }

    pydash.merge(defined_cols, pydash.pick(additional_cols, param_cols))
    mapped_tuples = map(lambda x: (x[0], pydash.get(data, x[1], None)), defined_cols.items())

    return dict(mapped_tuples)