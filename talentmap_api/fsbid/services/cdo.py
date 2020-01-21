import requests
import logging
import jwt
import talentmap_api.fsbid.services.common as services
from django.conf import settings
from talentmap_api.common.common_helpers import get_avatar_url

API_ROOT = settings.FSBID_API_URL

logger = logging.getLogger(__name__)

def cdo(jwt_token):
    '''
    Get All CDOs
    '''
    ad_id = jwt.decode(jwt_token, verify=False).get('unique_name')
    email = jwt.decode(jwt_token, verify=False).get('email')
    uri = f"Agents?ad_id={ad_id}&rl_cd=CDO"
    response = services.get_fsbid_results(uri, jwt_token, fsbid_cdo_list_to_talentmap_cdo_list, email)
    return response

def single_cdo(jwt_token = None, perdet_seq_num = None):
    '''
    Get a single client for a CDO
    '''
    ad_id = jwt.decode(jwt_token, verify=False).get('unique_name')
    email = jwt.decode(jwt_token, verify=False).get('email')
    uri = f"Agents?ad_id={ad_id}&rl_cd=CDO&request_params.perdet_seq_num={perdet_seq_num}"
    response = services.get_fsbid_results(uri, jwt_token, fsbid_cdo_list_to_talentmap_cdo_list, email)
    cdo = list(response)[0]
    initials = "".join([x for x in cdo['email'] if x.isupper()][:2][::-1])
    cdo['initials'] = initials
    avatar = get_avatar_url(cdo['email'])
    cdo['avatar'] = avatar
    return cdo

def fsbid_cdo_list_to_talentmap_cdo_list(data):
    return {
        "id": data.get("hru_id", None),
        "name": data.get("fullname", None),
        "email": data.get("email", None),
        "isCurrentUser": data.get("isCurrentUser", None),
    }
