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
    print("🐈🐈🐈🐈🐈🐈🐈🐈🐈🐈🐈🐈🐈🐈🐈🐈🐈🐈🐈🐈")
    print(panel)
    print("🐈🐈🐈🐈🐈🐈🐈🐈🐈🐈🐈🐈🐈🐈🐈🐈🐈🐈🐈🐈")

    return panel

def convert_panel_query(query):
    '''
    Converts TalentMap filters into FSBid filters
    '''
    values = {
        # Pagination
        "rp.pageNum": int(query.get("page", 1)),
        "rp.pageRows": query.get("limit", 5),
        # "rp.columns": None,
        # "rp.filter": services.convert_to_fsbid_ql('pmdmdtcode', query.get("pmd-dateCode", None)),
    }

    # TODO: how are we handling multiple passes to rp.filters?
    # TODO: handle sending in columns - what to call them?

    # a filter: pmdmdtcode|EQ|MEET|
    # a col: pmdmdtcode

    valuesToReturn = pydash.omit_by(values, lambda o: o is None or o == [])

    return urlencode(valuesToReturn, doseq=True, quote_via=quote)

def fsbid_panel_to_talentmap_panel(data):
    print("🐶🐶🐶🐶🐶🐶🐶🐶🐶🐶🐶🐶🐶🐶🐶🐶🐶")
    print(data)
    return {
        "pm_seq_num": pydash.get(data, "pmdpmseqnum", None),
        "pm_virtual": pydash.get(data, "pmvirtualind", None),
        "pm_create_id": pydash.get(data, "pmcreateid", None),
        "pm_create_date": pydash.get(data, "pmcreatedate", None),
        "pm_update_id": pydash.get(data, "pmupdateid", None),
        "pm_update_date": pydash.get(data, "pmupdatedate", None),
        "pmi_seq_num": pydash.get(data, "pmiseqnum", None),
        "pmi_official_num": pydash.get(data, "pmiofficialitemnum", None),
        "pmi_addendum": pydash.get(data, "pmiaddendumind", None),
        "pmi_label_text": pydash.get(data, "pmilabeltext", None),
        "pmi_create_id": pydash.get(data, "pmicreateid", None),
        "pmi_create_date": pydash.get(data, "pmicreatedate", None),
        "pmi_update_id": pydash.get(data, "pmiupdateid", None),
        "pmi_update_date": pydash.get(data, "pmiupdatedate", None),
        "pmt_code": pydash.get(data, "pmtcode", None),
        "pmt_desc_text": pydash.get(data, "pmtdesctext", None),
        "pmt_create_id": pydash.get(data, "pmtcreateid", None),
        "pmt_create_date": pydash.get(data, "pmtcreatedate", None),
        "pmt_update_id": pydash.get(data, "pmtupdateid", None),
        "pmt_update_date": pydash.get(data, "pmtupdatedate", None),
        "pms_code": pydash.get(data, "pmscode", None),
        "pms_desc_text": pydash.get(data, "pmsdesctext", None),
        "pms_create_id": pydash.get(data, "pmscreateid", None),
        "pms_create_date": pydash.get(data, "pmscreatedate", None),
        "pms_update_id": pydash.get(data, "pmsupdateid", None),
        "pms_update_date": pydash.get(data, "pmsupdatedate", None),
        "pmd_dttm": pydash.get(data, "pmddttm", None),
        "pmd_create_id": pydash.get(data, "pmdcreateid", None),
        "pmd_create_date": pydash.get(data, "pmdcreatedate", None),
        "pmd_update_id": pydash.get(data, "pmdupdateid", None),
        "pmd_update_date": pydash.get(data, "pmdupdatedate", None),
        "mdt_code": pydash.get(data, "mdtcode", None),
        "mdt_desc_text": pydash.get(data, "mdtdesctext", None),
        "mdt_include_time": pydash.get(data, "mdtincludetimeind", None),
        "mdt_user_input": pydash.get(data, "mdtuserinputind", None),
        "mdt_create_id": pydash.get(data, "mdtcreateid", None),
        "mdt_create_date": pydash.get(data, "mdtcreatedate", None),
        "mdt_update_id": pydash.get(data, "mdtupdateid", None),
        "mdt_update_date": pydash.get(data, "mdtupdatedate", None),
        "mic_code": pydash.get(data, "miccode", None),
        "mic_desc_text": pydash.get(data, "micdesctext", None),
        "mic_virtual_ind": pydash.get(data, "micvirtualallowedind", None),
        "mic_create_id": pydash.get(data, "miccreateid", None),
        "mic_create_date": pydash.get(data, "miccreatedate", None),
        "mic_update_id": pydash.get(data, "micupdateid", None),
        "mic_update_date": pydash.get(data, "micupdatedate", None),
    }
