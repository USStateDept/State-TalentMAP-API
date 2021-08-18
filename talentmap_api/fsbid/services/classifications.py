import logging
from urllib.parse import urlencode, quote
import pydash
import requests
from django.conf import settings

TP_ROOT = settings.TP_API_URL
BTP_ROOT = settings.BTP_API_URL

logger = logging.getLogger(__name__)

def get_client_classification(jwt_token=None, perdet_seq_num=None):
    '''
    Get the client's classification(s)
    '''
    from talentmap_api.fsbid.services.client import fsbid_classifications_to_tmap
    url = f"{BTP_ROOT}?request_params.perdet_seq_num={perdet_seq_num}"
    response = requests.get(url, headers={'JWTAuthorization': jwt_token, 'Content-Type': 'application/json'}, verify=False).json()  # nosec

    if response.get("Data") is None or response.get('return_code', -1) == -1:
        logger.error(f"Fsbid call to '{url}' failed.")
        return None

    return fsbid_classifications_to_tmap(response.get("Data", {}))

def insert_client_classification(jwt_token=None, perdet_seq_num=None, data=None):
    '''
    Inserts the client's classification(s)
    '''
    from talentmap_api.fsbid.services.client import fsbid_classifications_to_tmap
    values = {'te_id': data}
    te_id = urlencode({i: j for i, j in values.items() if j is not None}, doseq=True, quote_via=quote)
    uri = f"bidders?{te_id}&perdet_seq_num={perdet_seq_num}"
    url = f"{TP_ROOT}/{uri}"
    response = requests.post(url, headers={'JWTAuthorization': jwt_token, 'Content-Type': 'application/json'}, verify=False).json()  # nosec

    if response.get("Data") is None or response.get('return_code', -1) == -1:
        logger.error(f"Fsbid call to '{url}' failed.")
        return None

    return fsbid_classifications_to_tmap(response.get("Data", {}))


def delete_client_classification(jwt_token=None, perdet_seq_num=None, data=None):
    '''
    Deletes the client's classification(s)
    '''
    from talentmap_api.fsbid.services.client import fsbid_classifications_to_tmap
    values = {'te_id': data}
    te_id = urlencode({i: j for i, j in values.items() if j is not None}, doseq=True, quote_via=quote)
    uri = f"bidders?{te_id}&perdet_seq_num={perdet_seq_num}"
    url = f"{TP_ROOT}/{uri}"
    response = requests.delete(url, headers={'JWTAuthorization': jwt_token, 'Content-Type': 'application/json'}, verify=False).json()  # nosec

    if response.get("Data") is None or response.get('return_code', -1) == -1:
        logger.error(f"Fsbid call to '{url}' failed.")
        return None

    return fsbid_classifications_to_tmap(response.get("Data", {}))

def get_user_classifications(jwt_token=None, perdet_seq_num=None):
    '''
    Get the user's classification(s)
    '''
    from talentmap_api.fsbid.services.client import fsbid_classifications_to_tmap
    url = f"{BTP_ROOT}?request_params.perdet_seq_num={perdet_seq_num}"
    response = requests.get(url, headers={'JWTAuthorization': jwt_token, 'Content-Type': 'application/json'}, verify=False).json()  # nosec

    if response.get("Data") is None or response.get('return_code', -1) == -1:
        logger.error(f"Fsbid call to '{url}' failed.")
        return None
    return fsbid_classifications_to_tmap(response.get("Data", {}))
