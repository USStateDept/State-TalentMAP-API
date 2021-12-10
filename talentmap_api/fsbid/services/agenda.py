import logging
import jwt
import pydash
from functools import partial
from urllib.parse import urlencode, quote

from django.conf import settings

from talentmap_api.fsbid.services import common as services
from talentmap_api.common.common_helpers import ensure_date

AGENDA_ITEM_API_ROOT = settings.AGENDA_ITEM_API_URL

logger = logging.getLogger(__name__)


def get_single_agenda_item(jwt_token=None, ai_id = None):
    '''
    Get single agenda item
    '''
    args = {
        "uri": "",
        "id": ai_id,
        "query_mapping_function": None,
        "jwt_token": jwt_token,
        "mapping_function": fsbid_single_agenda_item_to_talentmap_single_agenda_item,
        "use_post": False,
        "api_root": AGENDA_ITEM_API_ROOT,
        "use_id": False,
    }

    agenda_item = services.get_individual(
        **args
    )

    return agenda_item


def get_agenda_items(jwt_token=None, query = {}, host=None):
    '''
    Get agenda items
    '''
    args = {
        "uri": "",
        "query": query,
        "query_mapping_function": convert_agenda_item_query,
        "jwt_token": jwt_token,
        "mapping_function": partial(fsbid_agenda_items_to_talentmap_agenda_items, jwt_token=jwt_token),
        "count_function": None,
        "base_url": "/api/v1/agenda_items/",
        "host": host,
        "use_post": False,
        "api_root": AGENDA_ITEM_API_ROOT,
    }

    agenda_items = services.send_get_request(
        **args
    )

    return agenda_items


def get_agenda_items_count(query, jwt_token, host=None, use_post=False):
    '''
    Gets the total number of agenda items for a filterset
    '''
    args = {
        "uri": "",
        "query": query,
        "query_mapping_function": convert_agenda_item_query,
        "jwt_token": jwt_token,
        "host": host,
        "use_post": False,
        "api_root": AGENDA_ITEM_API_ROOT,
    }
    return services.send_count_request(**args)


def convert_agenda_item_query(query):
    '''
    Converts TalentMap filters into FSBid filters
    '''
    values = {
        # Pagination
        "page_index": int(query.get("page", 1)),
        "page_size": query.get("limit", 1000),

        "order_by": query.get("ordering", None), # TODO - use services.sorting_values
        "filter": services.convert_to_fsbid_ql('perdetseqnum', query.get("perdet", None)),
    }

    valuesToReturn = pydash.omit_by(values, lambda o: o is None or o == [])

    return urlencode(valuesToReturn, doseq=True, quote_via=quote)


def fsbid_single_agenda_item_to_talentmap_single_agenda_item(data):

    return {
        "id": data.get("aiseqnum", None),
        "remarks": services.parse_agenda_remarks(data.get("aicombinedremarktext", '')),
        "panel_date": ensure_date(data.get("pmddttm", None), utc_offset=-5),
        "status": data.get("aisdesctext", None),
        "perdet": data.get("aiperdetseqnum", None),

        "legs": list(map(fsbid_legs_to_talentmap_legs, data.get("legs", []))), # Might be its own endpoint to fetch legs

        "update_date": ensure_date(data.get("update_date", None), utc_offset=-5), # TODO - find this date
        "modifier_name": data.get("aiupdateid", None), # TODO - this is only the id
        "creator_name": data.get("aiitemcreatorid", None), # TODO - this is only the id
    }


def fsbid_agenda_items_to_talentmap_agenda_items(data, jwt_token = None):
    ai_id = data.get("aiseqnum", None)

    agenda_item = get_single_agenda_item(jwt_token, ai_id)

    return {
        "id": data.get("aiseqnum", None),
        **agenda_item,
    }


def fsbid_legs_to_talentmap_legs(data):

    return {
        "id": data.get("ailaiseqnum", None),
        "pos_title": data.get("postitledesc", None),
        "pos_num": data.get("posseqnum", None),
        "org": data.get("posorgshortdesc", None),
        "eta": data.get("ailetadate", None),
        "ted": data.get("ailetdtedsepdate", None),
        "tod": data.get("ailtodothertext", None),
        "grade": data.get("posgradecode", None),
        "action": data.get("latabbrdesctext", None),

        "travel": data.get("travel", None), # TODO - find this text
    }