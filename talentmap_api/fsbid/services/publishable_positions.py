import logging
from urllib.parse import urlencode, quote

import pydash
from django.conf import settings

from talentmap_api.fsbid.services import common as services

PUBLISHABLE_POSITIONS_ROOT = settings.PUBLISHABLE_POSITIONS_API_URL

logger = logging.getLogger(__name__)


def get_capsule_description(id, jwt_token):
    '''
    Gets an individual capsule description 
    '''
    print('---inside service call ---')
    capsule_description = services.send_get_request(
        "capsule",
        {"id": id},
        convert_capsule_query,
        jwt_token,
        fsbid_capsule_to_talentmap_capsule,
        None,
        "/api/v1/fsbid/publishablePositions/",
        None,
        PUBLISHABLE_POSITIONS_ROOT
    )

    return pydash.get(capsule_description, 'results[0]') or None


def fsbid_capsule_to_talentmap_capsule(capsule):
    '''
    Formats FSBid response to Talentmap format 
    '''
    return {
        "id": capsule.get("pos_seq_num", None),
        "description": capsule.get("capsule_descr_txt", None),
        "last_updated_date": capsule.get("update_date", None),
        "updater_id": capsule.get("update_id", None),
    }


def convert_capsule_query(query):
    '''
    Converts TalentMap query to FSBid
    '''
    values = {
        f"pos_seq_num": query.get("id", None),
        f"ad_id": query.get("ad_id", None),
        f"update_date": query.get("last_updated_date", None),
        f"update_id": query.get("updater_id", None),
        f"capsule_descr_txt": query.get("description", None),
    }
    return urlencode({i: j for i, j in values.items() if j is not None}, doseq=True, quote_via=quote)

