import requests
import logging

from datetime import datetime

from django.conf import settings

from talentmap_api.common.common_helpers import ensure_date
import talentmap_api.fsbid.services.common as services

API_ROOT = settings.FSBID_API_URL

logger = logging.getLogger(__name__)

def get_bid_seasons(bsn_future_vacancy_ind, jwt_token):
    # set future vacancy indicator - default to 'Y'
    future_vacancy_ind = bsn_future_vacancy_ind if bsn_future_vacancy_ind else 'Y'
    url = f"{API_ROOT}/bidSeasons?future_vacancy_ind={future_vacancy_ind}"
    bid_seasons = requests.get(url, headers={'JWTAuthorization': jwt_token, 'Content-Type': 'application/json'}, verify=False).json()  # nosec
    return sorted(map(fsbid_bid_season_to_talentmap_bid_season, bid_seasons["Data"]), key=lambda k: k['description'])


def fsbid_bid_season_to_talentmap_bid_season(bs):
    return {
        "id": bs["bsn_id"],
        "description": bs["bsn_descr_text"],
        "start_date": ensure_date(bs["bsn_start_date"], utc_offset=-5),
        "end_date": ensure_date(bs["bsn_end_date"], utc_offset=-5),
        "panel_cut_off_date": ensure_date(bs["bsn_panel_cutoff_date"], utc_offset=-5)
    }