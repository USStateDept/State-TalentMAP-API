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
    print("🐈")
    args = {
        "uri": "",
        "query": query,
        "query_mapping_function": convert_panel_query,
        "jwt_token": jwt_token,
        "mapping_function": partial(fsbid_panel_to_talentmap_panel, jwt_token=jwt_token),
        "count_function": None,
        "base_url": "/api/v1/panel/",
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
    Converts TalentMap filters into FSBid filters
    '''
    values = {
        # Pagination
        "rp.pageNum": int(query.get("page", 1)),
        "rp.pageRows": query.get("limit", 1000),
        "rp.columns": None,
        "rp.filter": services.convert_to_fsbid_ql('pmdmdtcode', query.get("pmd-dateCode", None)),
    }
    # TODO: how are we handling multiple passes to rp.filters?
    # TODO: handle sending in columns - what to call them?

    # a filter: pmdmdtcode|EQ|MEET|
    # a col: pmdmdtcode

    valuesToReturn = pydash.omit_by(values, lambda o: o is None or o == [])

    return urlencode(valuesToReturn, doseq=True, quote_via=quote)

def fsbid_panel_to_talentmap_panel(data):

    return {
        "seqnum": pydash.get(data, "pmseqnum", None),
        "pmscode": pydash.get(data, "pmpmscode", None),
        "pmtcode": pydash.get(data, "pmpmtcode", None),
        "virtualind": pydash.get(data, "pmvirtualind", None),
        "createid": pydash.get(data, "pmcreateid", None),
        "createdate": pydash.get(data, "pmcreatedate", None),
        "updateid": pydash.get(data, "pmupdateid", None),
        "updatedate": pydash.get(data, "pmupdatedate", None),
        "pmiseqnum": pydash.get(data, "pmiseqnum", None),
        "pmimiccode": pydash.get(data, "pmimiccode", None),
        # "pmipmseqnum": pydash.get(data, "pmipmseqnum", None),
        "pmiofficialitemnum": pydash.get(data, "pmiofficialitemnum", None),
        "pmiaddendumind": pydash.get(data, "pmiaddendumind", None),
        "pmilabeltext": pydash.get(data, "pmilabeltext", None),
        "pmicreateid": pydash.get(data, "pmicreateid", None),
        "pmicreatedate": pydash.get(data, "pmicreatedate", None),
        "pmiupdateid": pydash.get(data, "pmiupdateid", None),
        "pmiupdatedate": pydash.get(data, "pmiupdatedate", None),
        # "pmtcode": pydash.get(data, "pmtcode", None),
        "pmtdesctext": pydash.get(data, "pmtdesctext", None),
        "pmtcreateid": pydash.get(data, "pmtcreateid", None),
        "pmtcreatedate": pydash.get(data, "pmtcreatedate", None),
        "pmtupdateid": pydash.get(data, "pmtupdateid", None),
        "pmtupdatedate": pydash.get(data, "pmtupdatedate", None),
        # "pmscode": pydash.get(data, "pmscode", None),
        "pmsdesctext": pydash.get(data, "pmsdesctext", None),
        "pmscreateid": pydash.get(data, "pmscreateid", None),
        "pmscreatedate": pydash.get(data, "pmscreatedate", None),
        "pmsupdateid": pydash.get(data, "pmsupdateid", None),
        "pmsupdatedate": pydash.get(data, "pmsupdatedate", None),
        "pmdpmseqnum": pydash.get(data, "pmdpmseqnum", None),
        "pmdmdtcode": pydash.get(data, "pmdmdtcode", None),
        "pmddttm": pydash.get(data, "pmddttm", None),
        "pmdcreateid": pydash.get(data, "pmdcreateid", None),
        "pmdcreatedate": pydash.get(data, "pmdcreatedate", None),
        "pmdupdateid": pydash.get(data, "pmdupdateid", None),
        "pmdupdatedate": pydash.get(data, "pmdupdatedate", None),
        "mdtcode": pydash.get(data, "mdtcode", None),
        "mdtdesctext": pydash.get(data, "mdtdesctext", None),
        "mdtincludetimeind": pydash.get(data, "mdtincludetimeind", None),
        "mdtuserinputind": pydash.get(data, "mdtuserinputind", None),
        "mdtordernum": pydash.get(data, "mdtordernum", None),
        "mdtcreateid": pydash.get(data, "mdtcreateid", None),
        "mdtcreatedate": pydash.get(data, "mdtcreatedate", None),
        "mdtupdateid": pydash.get(data, "mdtupdateid", None),
        "mdtupdatedate": pydash.get(data, "mdtupdatedate", None),
        "miccode": pydash.get(data, "miccode", None),
        "micdesctext": pydash.get(data, "micdesctext", None),
        "micordernum": pydash.get(data, "micordernum", None),
        "micvirtualallowedind": pydash.get(data, "micvirtualallowedind", None),
        "miccreateid": pydash.get(data, "miccreateid", None),
        "miccreatedate": pydash.get(data, "miccreatedate", None),
        "micupdateid": pydash.get(data, "micupdateid", None),
        "micupdatedate": pydash.get(data, "micupdatedate", None),
        "rnum": pydash.get(data, "rnum", None),
    }
